# 작업 관리 서비스 로직
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import Job, JobStep
from app.models.user import User
from app.models.video import Video
from app.models.billing import CreditUsage
from app.config import get_settings
from app.schemas import (
    JobStatus,
    ForgotPasswordResponse
)

settings = get_settings()


class JobService:
    """작업 관리 관련 서비스"""

    @staticmethod
    async def create_job(
        db: AsyncSession,
        user_id: str,
        job_type: str,
        video_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> Job:
        """새 작업 생성"""
        job = Job(
            user_id=user_id,
            video_id=video_id,
            job_type=job_type,
            status="pending",
            priority=priority,
            job_config=config or {}
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_job(
        db: AsyncSession,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Job]:
        """작업 조회"""
        query = select(Job).options(selectinload(Job.job_steps)).where(Job.id == job_id)
        
        if user_id:
            query = query.where(Job.user_id == user_id)
            
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_jobs_by_user(
        db: AsyncSession,
        user_id: str,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Job]:
        """사용자별 작업 목록 조회"""
        query = select(Job).where(Job.user_id == user_id)
        
        if job_type:
            query = query.where(Job.job_type == job_type)
        if status:
            query = query.where(Job.status == status)
            
        query = query.order_by(desc(Job.created_at)).offset(offset).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_jobs_by_video(
        db: AsyncSession,
        video_id: str,
        user_id: str
    ) -> List[Job]:
        """비디오별 작업 목록 조회"""
        result = await db.execute(
            select(Job)
            .where(
                and_(
                    Job.video_id == video_id,
                    Job.user_id == user_id
                )
            )
            .order_by(desc(Job.created_at))
        )
        return result.scalars().all()

    @staticmethod
    async def update_job_status(
        db: AsyncSession,
        job_id: str,
        status: str,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None
    ) -> bool:
        """작업 상태 업데이트"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return False

        job.status = status
        
        # 상태별 타이밍 업데이트
        if status == "processing" and not job.started_at:
            job.started_at = datetime.now(timezone.utc)
        elif status in ["completed", "failed", "cancelled"]:
            job.completed_at = datetime.now(timezone.utc)
            
        # 에러 정보 업데이트
        if error_message:
            job.error_message = error_message
        if error_code:
            job.error_code = error_code
            
        # 완료 시 진행률 100%로 설정
        if status == "completed":
            job.progress = 100.0
            
        job.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def update_job_progress(
        db: AsyncSession,
        job_id: str,
        progress: float,
        estimated_completion: Optional[datetime] = None
    ) -> bool:
        """작업 진행률 업데이트"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return False

        job.progress = max(0.0, min(100.0, progress))  # 0-100 범위로 제한
        
        if estimated_completion:
            job.estimated_completion = estimated_completion
            
        job.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def start_job(
        db: AsyncSession,
        job_id: str
    ) -> bool:
        """작업 시작"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job or job.status != "pending":
            return False

        job.status = "processing"
        job.started_at = datetime.now(timezone.utc)
        job.progress = 0.0
        job.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def complete_job(
        db: AsyncSession,
        job_id: str,
        result_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """작업 완료"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return False

        job.status = "completed"
        job.progress = 100.0
        job.completed_at = datetime.now(timezone.utc)
        
        if result_data:
            job.job_result = result_data
            
        job.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def fail_job(
        db: AsyncSession,
        job_id: str,
        error_message: str,
        error_code: Optional[str] = None,
        can_retry: bool = True
    ) -> bool:
        """작업 실패 처리"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return False

        job.status = "failed"
        job.completed_at = datetime.now(timezone.utc)
        job.error_message = error_message
        
        if error_code:
            job.error_code = error_code
            
        # 재시도 가능하고 최대 재시도 횟수 내라면 재시도 카운트 증가
        if can_retry and job.retry_count < job.max_retries:
            job.retry_count += 1
        
        job.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def cancel_job(
        db: AsyncSession,
        job_id: str,
        user_id: str
    ) -> bool:
        """작업 취소"""
        result = await db.execute(
            select(Job).where(
                and_(Job.id == job_id, Job.user_id == user_id)
            )
        )
        job = result.scalar_one_or_none()
        
        if not job or job.status in ["completed", "failed", "cancelled"]:
            return False

        job.status = "cancelled"
        job.completed_at = datetime.now(timezone.utc)
        job.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def retry_job(
        db: AsyncSession,
        job_id: str
    ) -> bool:
        """작업 재시도"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job or job.status != "failed" or job.retry_count >= job.max_retries:
            return False

        # 상태 초기화
        job.status = "pending"
        job.progress = 0.0
        job.started_at = None
        job.completed_at = None
        job.error_message = None
        job.error_code = None
        job.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def create_job_steps(
        db: AsyncSession,
        job_id: str,
        steps: List[Dict[str, Any]]
    ) -> bool:
        """작업 단계 생성"""
        job_steps = []
        for i, step_data in enumerate(steps):
            step = JobStep(
                job_id=job_id,
                step_name=step_data["name"],
                step_order=i + 1,
                status="pending"
            )
            job_steps.append(step)
            
        db.add_all(job_steps)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def update_step_status(
        db: AsyncSession,
        job_id: str,
        step_name: str,
        status: str,
        progress: float = 0.0,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """작업 단계 상태 업데이트"""
        result = await db.execute(
            select(JobStep).where(
                and_(
                    JobStep.job_id == job_id,
                    JobStep.step_name == step_name
                )
            )
        )
        step = result.scalar_one_or_none()
        
        if not step:
            return False

        step.status = status
        step.progress = max(0.0, min(100.0, progress))
        
        # 상태별 타이밍 업데이트
        if status == "processing" and not step.started_at:
            step.started_at = datetime.now(timezone.utc)
        elif status in ["completed", "failed", "skipped"]:
            step.completed_at = datetime.now(timezone.utc)
            
        if output_data:
            step.output_data = output_data
            
        if error_message:
            step.error_message = error_message
            
        step.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            
            # 전체 Job의 진행률도 업데이트
            await JobService._update_job_progress_from_steps(db, job_id)
            return True
        except Exception:
            await db.rollback()
            return False

    @staticmethod
    async def _update_job_progress_from_steps(
        db: AsyncSession,
        job_id: str
    ) -> None:
        """작업 단계들의 진행률을 기반으로 전체 Job 진행률 업데이트"""
        # 모든 단계의 평균 진행률 계산
        result = await db.execute(
            select(func.avg(JobStep.progress))
            .where(JobStep.job_id == job_id)
        )
        avg_progress = result.scalar() or 0.0
        
        # Job 진행률 업데이트
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        
        if job:
            job.progress = avg_progress
            job.updated_at = datetime.now(timezone.utc)
            await db.commit()

    @staticmethod
    async def get_job_status_for_video(
        db: AsyncSession,
        video_id: str,
        user_id: str
    ) -> Optional[JobStatus]:
        """비디오의 최신 작업 상태 조회"""
        result = await db.execute(
            select(Job)
            .where(
                and_(
                    Job.video_id == video_id,
                    Job.user_id == user_id
                )
            )
            .order_by(desc(Job.created_at))
            .limit(1)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return None

        return JobStatus(
            job_id=job.id,
            status=job.status,
            progress=job.progress,
            estimated_completion=job.estimated_completion,
            error_message=job.error_message
        )

    @staticmethod
    async def cleanup_old_jobs(
        db: AsyncSession,
        days_old: int = 30
    ) -> int:
        """오래된 완료/실패 작업 정리"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        result = await db.execute(
            select(Job).where(
                and_(
                    Job.status.in_(["completed", "failed", "cancelled"]),
                    Job.completed_at < cutoff_date
                )
            )
        )
        old_jobs = result.scalars().all()
        
        for job in old_jobs:
            await db.delete(job)
            
        try:
            await db.commit()
            return len(old_jobs)
        except Exception:
            await db.rollback()
            return 0

    @staticmethod
    async def get_pending_jobs(
        db: AsyncSession,
        job_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Job]:
        """대기 중인 작업 조회 (작업 큐용)"""
        query = select(Job).where(Job.status == "pending")
        
        if job_type:
            query = query.where(Job.job_type == job_type)
            
        query = query.order_by(Job.priority.asc(), Job.created_at.asc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def record_credit_usage(
        db: AsyncSession,
        job: Job,
        credits_used: int,
        operation_type: str,
        description: Optional[str] = None
    ) -> bool:
        """크레딧 사용량 기록"""
        current_month = datetime.now(timezone.utc).strftime('%Y-%m')
        
        credit_usage = CreditUsage(
            user_id=job.user_id,
            video_id=job.video_id,
            job_id=job.id,
            credits_used=credits_used,
            operation_type=operation_type,
            description=description or f"{job.job_type} 작업",
            usage_month=current_month
        )
        
        # Job에도 비용 기록
        job.credits_cost = credits_used
        
        db.add(credit_usage)
        
        try:
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False