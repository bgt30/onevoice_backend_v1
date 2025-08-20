# AI 더빙 파이프라인 오케스트레이션 서비스
import os
import shutil
import asyncio
import importlib
import tempfile
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.video import Video
from app.models.user import User
from app.services.job_service import JobService
from app.services.storage_service import storage_service
from app.services.notification_service import NotificationService
from app.config import get_settings
from app.schemas import DubRequest, DubResponse

settings = get_settings()
logger = logging.getLogger(__name__)


class DubbingService:
    """AI 더빙 파이프라인 오케스트레이션 서비스
    
    이 서비스는 순수한 오케스트레이션 & 인프라 역할만 담당합니다:
    - 작업공간 관리
    - 파일 입출력 관리  
    - 진행률 추적
    - 에러 처리 & 알림
    - 결과물 업로드
    
    AI 모듈들은 순수한 데이터 처리 로직만 담당하며, 이 서비스가 오케스트레이션합니다.
    """

    # 15단계 더빙 파이프라인 정의
    DUBBING_STEPS = [
        {
            "name": "prepare_video",
            "module": "ai._1_find_video",
            "function": "find_video_files",
            "weight": 3,
            "description": "비디오 파일 준비"
        },
        {
            "name": "speech_recognition",
            "module": "ai._2_asr", 
            "function": "transcribe",
            "weight": 15,
            "description": "음성 인식 및 전사"
        },
        {
            "name": "nlp_split",
            "module": "ai._3_1_split_nlp",
            "function": "split_by_spacy", 
            "weight": 5,
            "description": "NLP 기반 텍스트 분할"
        },
        {
            "name": "meaning_split",
            "module": "ai._3_2_split_meaning",
            "function": "split_sentences_by_meaning",
            "weight": 5,
            "description": "의미 기반 텍스트 분할"
        },
        {
            "name": "summarize",
            "module": "ai._4_1_summarize",
            "function": "get_summary",
            "weight": 8,
            "description": "요약 및 용어 추출"
        },
        {
            "name": "translate",
            "module": "ai._4_2_translate",
            "function": "translate_all", 
            "weight": 15,
            "description": "텍스트 번역"
        },
        {
            "name": "split_subtitles",
            "module": "ai._5_split_sub",
            "function": "split_for_sub_main",
            "weight": 5,
            "description": "자막용 텍스트 분할"
        },
        {
            "name": "generate_subtitles",
            "module": "ai._6_gen_sub", 
            "function": "align_timestamp_main",
            "weight": 8,
            "description": "자막 생성 및 타임스탬프 정렬"
        },
        {
            "name": "embed_subtitles",
            "module": "ai._7_sub_into_vid",
            "function": "merge_subtitles_to_video",
            "weight": 5,
            "description": "자막을 비디오에 삽입"
        },
        {
            "name": "audio_task_setup",
            "module": "ai._8_1_audio_task",
            "function": "gen_audio_task_main",
            "weight": 5,
            "description": "오디오 작업 설정"
        },
        {
            "name": "dub_chunks",
            "module": "ai._8_2_dub_chunks",
            "function": "gen_dub_chunks",
            "weight": 5,
            "description": "더빙 청크 생성"
        },
        {
            "name": "extract_reference_audio",
            "module": "ai._9_refer_audio",
            "function": "extract_refer_audio_main",
            "weight": 3,
            "description": "참조 오디오 추출"
        },
        {
            "name": "generate_audio",
            "module": "ai._10_gen_audio",
            "function": "gen_audio",
            "weight": 15,
            "description": "TTS 오디오 생성"
        },
        {
            "name": "merge_audio",
            "module": "ai._11_merge_audio",
            "function": "merge_full_audio",
            "weight": 5,
            "description": "오디오 병합"
        },
        {
            "name": "final_video",
            "module": "ai._12_dub_to_vid",
            "function": "merge_video_audio",
            "weight": 8,
            "description": "최종 비디오 생성"
        }
    ]

    @staticmethod
    async def start_dubbing_job(
        db: AsyncSession,
        user: User,
        video_id: str,
        dub_request: DubRequest
    ) -> DubResponse:
        """더빙 작업 시작(등록/과금/상태 전이 포함)"""
        from sqlalchemy import select as _select, and_ as _and_, desc as _desc
        from app.models.video import Video as _Video, MediaFile as _MediaFile

        # 비디오 검증
        result = await db.execute(
            _select(_Video).where(
                _and_(_Video.id == video_id, _Video.user_id == user.id)
            )
        )
        video = result.scalar_one_or_none()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="비디오를 찾을 수 없습니다.")

        if video.status not in ["uploaded", "completed"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="업로드되거나 완료된 비디오만 더빙 가능합니다.")

        # Job 설정
        job_config = {
            "target_language": dub_request.target_language,
            "voice_id": dub_request.voice_id,
            "preserve_background_music": dub_request.preserve_background_music,
            "tts_method": "openai_tts",
        }

        try:
            # Job 생성
            job = await JobService.create_job(
                db=db,
                user_id=user.id,
                job_type="dubbing",
                video_id=video_id,
                config=job_config,
            )

            # 비디오 상태 전이
            video.status = "processing"
            video.processing_started_at = datetime.now(timezone.utc)
            video.updated_at = datetime.now(timezone.utc)

            # 원본 MediaFile 조회하여 크레딧 산정
            mf_res = await db.execute(
                _select(_MediaFile).where(
                    _and_(
                        _MediaFile.video_id == video.id,
                        _MediaFile.file_type == "original",
                        _MediaFile.is_active == True,
                    )
                ).order_by(_desc(_MediaFile.created_at)).limit(1)
            )
            original_mf = mf_res.scalar_one_or_none()
            vid_duration = original_mf.duration if (original_mf and original_mf.duration) else 1
            credits_used = settings.CREDIT_COST_PER_MINUTE * int(vid_duration)

            await JobService.record_credit_usage(
                db=db,
                job=job,
                credits_used=credits_used,
                operation_type="dubbing",
                description=f"더빙 작업: {video.title}",
            )

            # 변경사항 커밋
            await db.commit()

            return DubResponse(job_id=job.id, message="더빙 작업이 시작되었습니다.")
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="더빙 작업 시작 중 오류가 발생했습니다.")

    @staticmethod
    async def execute_dubbing_pipeline(job_id: str) -> None:
        """더빙 파이프라인 실행 (오케스트레이션)"""
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import get_async_session
        
        async with get_async_session() as db:
            try:
                # 1. 작업 정보 조회
                job = await JobService.get_job(db, job_id)
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                logger.info(f"Starting dubbing pipeline for job {job_id}")
                
                # 2. 작업공간 설정 (인프라)
                workspace = await DubbingService._setup_workspace(job)
                logger.info(f"Workspace created: {workspace}")
                
                # 3. 소스 비디오 다운로드 (파일 I/O)
                await DubbingService._download_source_video(job, workspace)
                logger.info("Source video downloaded")
                
                # 4. 설정 파일 복사 (파일 I/O)
                await DubbingService._copy_config_files(workspace)
                logger.info("Config files copied")
                
                # 5. 작업 단계 생성 (진행률 추적)
                await DubbingService._create_job_steps(db, job_id)
                logger.info("Job steps created")
                
                # 6. 각 AI 모듈 실행 (오케스트레이션)
                for step_config in DubbingService.DUBBING_STEPS:
                    await DubbingService._execute_step(db, job_id, step_config, workspace)
                    logger.info(f"Step completed: {step_config['name']}")
                
                # 7. 최종 처리 (결과물 업로드)
                await DubbingService._finalize_dubbing(db, job, workspace)
                logger.info("Dubbing pipeline completed successfully")
                
            except Exception as e:
                logger.error(f"Dubbing pipeline failed for job {job_id}: {str(e)}")
                await DubbingService._handle_pipeline_error(db, job_id, str(e))
                raise

    @staticmethod
    async def resume_dubbing_pipeline(job_id: str) -> None:
        """더빙 파이프라인 재개 (오케스트레이션)"""
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import get_async_session
        
        async with get_async_session() as db:
            try:
                # 1. 작업 정보 조회
                job = await JobService.get_job(db, job_id)
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                logger.info(f"Resuming dubbing pipeline for job {job_id}")

                # 1-1. 상태 초기화 (실패에서 재개 시)
                try:
                    job.status = "processing"
                    if not job.started_at:
                        job.started_at = datetime.now(timezone.utc)
                    job.error_message = None
                    job.error_code = None
                    job.updated_at = datetime.now(timezone.utc)
                    await db.commit()
                except Exception as _e:
                    await db.rollback()
                    logger.warning(f"Failed to reset job state for resume: {str(_e)}")
                
                # 2. 작업공간 경로 확인
                workspace = f"workspaces/{job_id}"
                if not os.path.exists(workspace):
                    logger.info(f"Workspace not found for job {job_id}. Recreating workspace and redownloading source video.")
                    workspace = await DubbingService._setup_workspace(job)
                    # 소스 비디오 재다운로드 및 설정 파일 복사
                    await DubbingService._download_source_video(job, workspace)
                    await DubbingService._copy_config_files(workspace)
                
                # 3. 실패한 단계부터 재개
                from sqlalchemy import select
                from app.models.job import JobStep
                
                result = await db.execute(
                    select(JobStep).where(JobStep.job_id == job_id)
                )
                steps = result.scalars().all()
                
                # 실패한 단계 찾기 및 상태 정리
                failed_steps = [step for step in steps if step.status == "failed"]
                if failed_steps:
                    # 실패 단계 상태 초기화
                    for s in failed_steps:
                        s.status = "pending"
                        s.progress = 0.0
                        s.started_at = None
                        s.completed_at = None
                        s.error_message = None
                    await db.commit()

                # 재실행 대상 결정: 실패 단계가 없으면 전체 재실행
                if not failed_steps:
                    logger.info(f"No failed steps found. Rerunning full pipeline for job {job_id}.")
                    steps_to_run = DubbingService.DUBBING_STEPS
                else:
                    # 실패한 개별 단계만 재실행 (정책상 필요한 경우 전체 재실행으로 변경 가능)
                    steps_to_run = []
                    for failed_step in failed_steps:
                        cfg = next((s for s in DubbingService.DUBBING_STEPS if s["name"] == failed_step.step_name), None)
                        if cfg:
                            steps_to_run.append(cfg)

                # 진행률 일관성 정리: 현재 단계 기준으로 재계산
                try:
                    await DubbingService._update_overall_progress(db, job_id)
                except Exception as _e:
                    logger.warning(f"Failed to recalc overall progress before resume: {str(_e)}")

                # 단계 실행 루프(취소 상태 체크 포함)
                for step_config in steps_to_run:
                    # 취소 상태 확인 (동시성 안전)
                    try:
                        from sqlalchemy import select as _select
                        job_row = (await db.execute(_select(Job).where(Job.id == job_id))).scalar_one_or_none()
                        if job_row and job_row.status == "cancelled":
                            logger.info(f"Job {job_id} is cancelled. Stopping resume.")
                            return
                    except Exception as _e:
                        logger.warning(f"Failed to check cancel state before step {step_config['name']}: {str(_e)}")

                    await DubbingService._execute_step(db, job_id, step_config, workspace)
                    logger.info(f"Resumed step: {step_config['name']}")
                
                # 4. 최종 처리
                await DubbingService._finalize_dubbing(db, job, workspace)
                logger.info("Dubbing pipeline resumed successfully")
                
            except Exception as e:
                logger.error(f"Resume dubbing pipeline failed for job {job_id}: {str(e)}")
                await DubbingService._handle_pipeline_error(db, job_id, str(e))
                raise

    @staticmethod
    async def _setup_workspace(job: Job) -> str:
        """작업공간 설정 (인프라)"""
        workspace = f"workspaces/{job.id}"
        
        # 작업공간 디렉토리 생성
        os.makedirs(workspace, exist_ok=True)
        os.makedirs(f"{workspace}/output", exist_ok=True)
        os.makedirs(f"{workspace}/output/log", exist_ok=True)
        os.makedirs(f"{workspace}/output/audio", exist_ok=True)
        os.makedirs(f"{workspace}/output/audio/refers", exist_ok=True)
        os.makedirs(f"{workspace}/output/audio/segs", exist_ok=True)
        os.makedirs(f"{workspace}/output/audio/tmp", exist_ok=True)
        
        return workspace

    @staticmethod
    async def _download_source_video(job: Job, workspace: str) -> None:
        """소스 비디오 다운로드 (파일 I/O)"""
        try:
            # 스토리지에서 비디오 파일 다운로드
            import os as _os
            # MediaFile에서 원본 조회
            from sqlalchemy import select as _select, desc as _desc
            from app.models.video import MediaFile as _MediaFile
            from app.core.database import get_async_session as _get_async_session
            async with _get_async_session() as _db:
                mf_res = await _db.execute(
                _select(_MediaFile).where(
                    _MediaFile.video_id == job.video_id,
                    _MediaFile.file_type == "original",
                    _MediaFile.is_active == True,
                ).order_by(_desc(_MediaFile.created_at)).limit(1)
                )
                original_mf = mf_res.scalar_one_or_none()
            if not original_mf or not original_mf.s3_key:
                raise Exception("원본 MediaFile을 찾을 수 없거나 s3_key가 없습니다.")

            original_name = _os.path.basename(original_mf.s3_key) if original_mf.s3_key else "source.mp4"
            video_path = f"{workspace}/output/{original_name}"
            await storage_service.download_file(original_mf.s3_key, video_path)
            
            logger.info(f"Source video downloaded to {video_path}")
            
        except Exception as e:
            logger.error(f"Failed to download source video: {str(e)}")
            raise Exception(f"소스 비디오 다운로드 실패: {str(e)}")

    @staticmethod
    async def _copy_config_files(workspace: str) -> None:
        """설정 파일 복사 (파일 I/O)"""
        try:
            # 기본 설정 파일 복사
            config_source = "config.yaml"
            config_dest = f"{workspace}/config.yaml"
            
            if os.path.exists(config_source):
                shutil.copy2(config_source, config_dest)
                logger.info(f"Config file copied to {config_dest}")
            else:
                logger.warning("Default config file not found")
            
            # 커스텀 용어 파일 복사 (있는 경우)
            custom_terms_source = "custom_terms.xlsx"
            custom_terms_dest = f"{workspace}/custom_terms.xlsx"
            
            if os.path.exists(custom_terms_source):
                shutil.copy2(custom_terms_source, custom_terms_dest)
                logger.info(f"Custom terms file copied to {custom_terms_dest}")
                
        except Exception as e:
            logger.error(f"Failed to copy config files: {str(e)}")
            raise Exception(f"설정 파일 복사 실패: {str(e)}")

    @staticmethod
    async def _create_job_steps(db: AsyncSession, job_id: str) -> None:
        """작업 단계 생성 (진행률 추적)"""
        from app.models.job import JobStep
        
        for step_config in DubbingService.DUBBING_STEPS:
            step = JobStep(
                job_id=job_id,
                step_name=step_config["name"],
                status="pending",
                progress=0.0,
                weight=step_config["weight"],
                description=step_config["description"]
            )
            db.add(step)
        
        await db.commit()

    @staticmethod
    async def _execute_step(db: AsyncSession, job_id: str, step_config: Dict[str, Any], workspace: str) -> None:
        """개별 파이프라인 단계 실행 (오케스트레이션)"""
        step_name = step_config["name"]
        
        try:
            logger.info(f"Starting step: {step_name}")
            
            # 단계 시작 (진행률 추적)
            await JobService.update_step_status(
                db, job_id, step_name, "processing", 0.0
            )
            
            # AI 모듈 실행 (오케스트레이션)
            await DubbingService._run_ai_module(step_config, workspace)
            
            # 단계 완료 (진행률 추적)
            await JobService.update_step_status(
                db, job_id, step_name, "completed", 100.0
            )
            
            # 전체 진행률 업데이트 (진행률 추적)
            await DubbingService._update_overall_progress(db, job_id)
            
            logger.info(f"Step completed: {step_name}")
            
        except Exception as e:
            logger.error(f"Step failed: {step_name} - {str(e)}")
            
            # 단계 실패 (에러 처리)
            await JobService.update_step_status(
                db, job_id, step_name, "failed", 0.0,
                error_message=str(e)
            )
            
            # 알림 발송 (알림)
            await DubbingService._send_error_notification(job_id, step_name, str(e))
            
            raise Exception(f"{step_name} 단계 실패: {str(e)}")

    @staticmethod
    async def _run_ai_module(step_config: Dict[str, Any], workspace: str) -> None:
        """AI 모듈 실행 (오케스트레이션)"""
        try:
            # 동적 모듈 import
            module = importlib.import_module(step_config["module"])
            function = getattr(module, step_config["function"])
            
            # config 파일 경로 설정
            from ai.utils.workspace_utils import get_workspace_config_path
            config_path = get_workspace_config_path(workspace)
            
            # 함수 시그니처 확인하여 적절한 매개변수 전달
            import inspect
            sig = inspect.signature(function)
            params = list(sig.parameters.keys())
            
            if len(params) == 0:
                # 매개변수가 없는 경우 (legacy 함수)
                if asyncio.iscoroutinefunction(function):
                    await function()
                else:
                    await asyncio.to_thread(function)
            else:
                # 매개변수가 있는 경우 (새로운 함수)
                kwargs = {
                    'workspace_path': workspace,
                    'config_path': config_path
                }
                
                # 실제 함수가 받는 매개변수만 전달
                call_kwargs = {k: v for k, v in kwargs.items() if k in params}
                
                if asyncio.iscoroutinefunction(function):
                    await function(**call_kwargs)
                else:
                    await asyncio.to_thread(function, **call_kwargs)
                
        except Exception as e:
            logger.error(f"AI module execution failed: {step_config['module']}.{step_config['function']} - {str(e)}")
            raise Exception(f"AI 모듈 실행 실패 ({step_config['module']}.{step_config['function']}): {str(e)}")

    @staticmethod
    async def _update_overall_progress(db: AsyncSession, job_id: str) -> None:
        """전체 진행률 업데이트를 JobService의 가중치 기반 로직으로 위임"""
        try:
            await JobService._update_job_progress_from_steps(db, job_id)
            logger.info("Overall progress updated via JobService (weighted)")
        except Exception as e:
            logger.error(f"Failed to update overall progress (delegated): {str(e)}")
            raise Exception(f"전체 진행률 업데이트 실패: {str(e)}")

    @staticmethod
    async def _finalize_dubbing(db: AsyncSession, job: Job, workspace: str) -> None:
        """더빙 완료 처리 (결과물 업로드)"""
        try:
            logger.info("Finalizing dubbing process")
            
            # 1. 결과 파일 업로드 (결과물 업로드)
            result_files = await DubbingService._upload_result_files(db, job, workspace)
            
            # 2. 비디오 상태 업데이트 (진행률 추적)
            await DubbingService._update_video_status(db, job, result_files)
            
            # 3. 작업 완료 처리 (진행률 추적)
            await JobService.update_job_status(db, job.id, "completed")
            
            # 4. 완료 알림 발송 (알림)
            await DubbingService._send_completion_notification(job.id)
            
            # 5. 작업공간 정리 (인프라)
            await DubbingService._cleanup_workspace(workspace)
            
            logger.info("Dubbing finalized successfully")
            
        except Exception as e:
            logger.error(f"Failed to finalize dubbing: {str(e)}")
            raise Exception(f"더빙 완료 처리 실패: {str(e)}")

    @staticmethod
    async def _upload_result_files(db: AsyncSession, job: Job, workspace: str) -> Dict[str, str]:
        """결과 파일 업로드 (결과물 업로드)"""
        result_files = {}
        
        try:
            # 업로드할 파일들 정의
            files_to_upload = [
                ("output/output_dub.mp4", "dubbed_video"),
                ("output/output_sub.mp4", "subtitle_video"),
                ("output/dub.srt", "dub_subtitles"),
                ("output/trans.srt", "translation_subtitles"),
                ("output/src.srt", "source_subtitles")
            ]
            
            for file_path, file_type in files_to_upload:
                full_path = f"{workspace}/{file_path}"
                if os.path.exists(full_path):
                    # 스토리지에 업로드 (로컬 파일 업로드)
                    storage_key = f"results/{job.id}/{os.path.basename(file_path)}"
                    uploaded_url = await storage_service.upload_local_file(full_path, storage_key)
                    result_files[file_type] = storage_key
                    logger.info(f"Uploaded {file_type}: {storage_key}")

                    # MediaFile 레코드 생성
                    from app.models.video import MediaFile as _MediaFile
                    import os as _os
                    filename = _os.path.basename(full_path)
                    file_ext = _os.path.splitext(filename)[1].lower().lstrip('.') or 'bin'
                    try:
                        local_size = _os.path.getsize(full_path)
                    except Exception:
                        local_size = None

                    media_file = _MediaFile(
                        video_id=job.video_id,
                        filename=filename,
                        file_type=file_type,
                        file_format=file_ext,
                        file_size=local_size,
                        file_path=storage_key,
                        s3_bucket=settings.S3_BUCKET_NAME,
                        s3_key=storage_key,
                        public_url=uploaded_url,
                        language_code=job.target_language,
                        voice_id=job.voice_id,
                        is_active=True,
                        extra_metadata={
                            "job_id": job.id,
                            "workspace": workspace
                        }
                    )
                    db.add(media_file)
                else:
                    logger.warning(f"Result file not found: {full_path}")
            
            await db.commit()
            return result_files
            
        except Exception as e:
            logger.error(f"Failed to upload result files: {str(e)}")
            await db.rollback()
            raise Exception(f"결과 파일 업로드 실패: {str(e)}")

    @staticmethod
    async def _update_video_status(db: AsyncSession, job: Job, result_files: Dict[str, str]) -> None:
        """비디오 상태 업데이트 (진행률 추적)"""
        try:
            # 산출물 경로는 MediaFile에서 관리하므로 Video의 *_path는 더 이상 쓰지 않음
            job.video.status = "completed"
            job.video.processing_completed_at = datetime.now(timezone.utc)
            
            await db.commit()
            logger.info("Video status updated")
            
        except Exception as e:
            logger.error(f"Failed to update video status: {str(e)}")
            raise Exception(f"비디오 상태 업데이트 실패: {str(e)}")

    @staticmethod
    async def _send_completion_notification(job_id: str) -> None:
        """완료 알림 발송 (알림)"""
        try:
            notification_service = NotificationService()
            await notification_service.send_job_completion_notification(job_id)
            logger.info(f"Completion notification sent for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to send completion notification: {str(e)}")

    @staticmethod
    async def _send_error_notification(job_id: str, step_name: str, error_message: str) -> None:
        """에러 알림 발송 (알림)"""
        try:
            notification_service = NotificationService()
            await notification_service.send_job_error_notification(job_id, step_name, error_message)
            logger.info(f"Error notification sent for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")

    @staticmethod
    async def _handle_pipeline_error(db: AsyncSession, job_id: str, error_message: str) -> None:
        """파이프라인 에러 처리 (에러 처리)"""
        try:
            # 작업 상태를 실패로 업데이트
            await JobService.update_job_status(db, job_id, "failed", error_message)
            
            # 에러 알림 발송
            await DubbingService._send_error_notification(job_id, "pipeline", error_message)
            
            logger.error(f"Pipeline error handled for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle pipeline error: {str(e)}")

    @staticmethod
    async def _cleanup_workspace(workspace: str) -> None:
        """작업공간 정리 (인프라)"""
        try:
            if os.path.exists(workspace):
                shutil.rmtree(workspace)
                logger.info(f"Workspace cleaned up: {workspace}")
        except Exception as e:
            logger.error(f"Failed to cleanup workspace: {str(e)}")

    @staticmethod
    async def cancel_dubbing_job(db: AsyncSession, job_id: str, user_id: str) -> bool:
        """더빙 작업 취소 (오케스트레이션)"""
        try:
            # 작업 정보 조회
            job = await JobService.get_job(db, job_id)
            if not job:
                return False
            
            # 사용자 권한 확인
            if job.user_id != user_id:
                return False
            
            # 작업 상태를 취소로 업데이트
            await JobService.update_job_status(db, job_id, "cancelled")
            
            # 작업공간 정리
            workspace = f"workspaces/{job_id}"
            await DubbingService._cleanup_workspace(workspace)
            
            # 취소 알림 발송
            notification_service = NotificationService()
            await notification_service.send_job_cancellation_notification(job_id)
            
            logger.info(f"Job cancelled: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {str(e)}")
            return False