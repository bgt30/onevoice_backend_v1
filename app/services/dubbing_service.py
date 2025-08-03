# AI 더빙 파이프라인 서비스
import os
import shutil
import asyncio
import importlib
import tempfile
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

settings = get_settings()


class DubbingService:
    """AI 더빙 파이프라인 관리 서비스"""

    # 15단계 더빙 파이프라인 정의
    DUBBING_STEPS = [
        {
            "name": "prepare_video",
            "module": "ai._1_ytdlp",
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
            "name": "create_dub_chunks", 
            "module": "ai._8_2_dub_chunks",
            "function": "gen_dub_chunks",
            "weight": 8,
            "description": "더빙 청크 생성"
        },
        {
            "name": "reference_audio",
            "module": "ai._9_refer_audio",
            "function": "extract_refer_audio_main",
            "weight": 5,
            "description": "참조 오디오 추출"
        },
        {
            "name": "generate_audio",
            "module": "ai._10_gen_audio",
            "function": "gen_audio",
            "weight": 20,
            "description": "TTS 오디오 생성"
        },
        {
            "name": "merge_audio",
            "module": "ai._11_merge_audio", 
            "function": "merge_full_audio",
            "weight": 10,
            "description": "오디오 병합"
        },
        {
            "name": "finalize_video",
            "module": "ai._12_dub_to_vid",
            "function": "merge_video_audio",
            "weight": 8,
            "description": "최종 더빙 비디오 생성"
        }
    ]

    @staticmethod
    async def execute_dubbing_pipeline(job_id: str) -> None:
        """메인 더빙 파이프라인 실행"""
        db = None
        workspace = None
        original_cwd = os.getcwd()
        
        try:
            # DB 세션 생성
            from app.core.database import get_async_session
            async for session in get_async_session():
                db = session
                break
            
            # Job 조회
            job = await JobService.get_job(db, job_id)
            if not job:
                raise Exception(f"Job {job_id}를 찾을 수 없습니다.")
            
            # Job 시작
            await JobService.start_job(db, job_id)
            
            # 작업 공간 설정
            workspace = await DubbingService._setup_workspace(job)
            os.chdir(workspace)
            
            # AI 설정 준비
            await DubbingService._prepare_ai_config(job)
            
            # Job Steps 생성
            await DubbingService._create_job_steps(db, job_id)
            
            # 파이프라인 실행
            for step in DubbingService.DUBBING_STEPS:
                await DubbingService._execute_step(db, job_id, step, workspace)
            
            # 결과물 업로드 및 완료 처리
            await DubbingService._finalize_dubbing(db, job, workspace)
            
        except Exception as e:
            if db:
                await JobService.fail_job(
                    db, job_id, 
                    f"더빙 작업 실패: {str(e)}", 
                    "DUBBING_ERROR"
                )
                
                # 영상 처리 실패 알림 발송
                try:
                    job = await JobService.get_job(db, job_id)
                    if job and job.video_id:
                        # 비디오 정보 조회
                        from sqlalchemy import select
                        video_result = await db.execute(select(Video).where(Video.id == job.video_id))
                        video = video_result.scalar_one_or_none()
                        
                        # 사용자 정보 조회
                        user_result = await db.execute(select(User).where(User.id == job.user_id))
                        user = user_result.scalar_one_or_none()
                        
                        if video and user:
                            # 재시도 URL
                            retry_url = f"{settings.FRONTEND_URL}/videos/{video.id}/dub"
                            
                            await NotificationService.send_video_processing_failed_notification(
                                user=user,
                                video_title=video.title,
                                error_message=str(e),
                                retry_url=retry_url
                            )
                except Exception as notification_error:
                    # 알림 발송 실패해도 무시
                    print(f"영상 처리 실패 알림 발송 실패: {str(notification_error)}")
            raise e
            
        finally:
            # 정리
            os.chdir(original_cwd)
            if workspace and os.path.exists(workspace):
                try:
                    shutil.rmtree(workspace)
                except Exception:
                    pass  # 정리 실패해도 무시

    @staticmethod
    async def resume_dubbing_pipeline(job_id: str) -> None:
        """중단된 더빙 파이프라인 재개"""
        db = None
        
        try:
            from app.core.database import get_async_session
            async for session in get_async_session():
                db = session
                break
                
            # Job과 JobStep 상태 확인
            job = await JobService.get_job(db, job_id)
            if not job:
                return
                
            # processing 상태면 재시작
            if job.status == "processing":
                await JobService.update_job_status(db, job_id, "pending")
                await DubbingService.execute_dubbing_pipeline(job_id)
                
        except Exception as e:
            if db:
                await JobService.fail_job(
                    db, job_id,
                    f"더빙 작업 재개 실패: {str(e)}",
                    "RESUME_ERROR"
                )
                
                # 영상 처리 실패 알림 발송 (재개 실패)
                try:
                    job = await JobService.get_job(db, job_id)
                    if job and job.video_id:
                        from sqlalchemy import select
                        video_result = await db.execute(select(Video).where(Video.id == job.video_id))
                        video = video_result.scalar_one_or_none()
                        
                        # 사용자 정보 조회
                        user_result = await db.execute(select(User).where(User.id == job.user_id))
                        user = user_result.scalar_one_or_none()
                        
                        if video and user:
                            retry_url = f"{settings.FRONTEND_URL}/videos/{video.id}/dub"
                            
                            await NotificationService.send_video_processing_failed_notification(
                                user=user,
                                video_title=video.title,
                                error_message=f"작업 재개 중 오류 발생: {str(e)}",
                                retry_url=retry_url
                            )
                except Exception:
                    pass  # 알림 발송 실패해도 무시

    @staticmethod
    async def _setup_workspace(job: Job) -> str:
        """작업 공간 설정"""
        # 임시 작업 디렉터리 생성
        workspace = tempfile.mkdtemp(prefix=f"dubbing_{job.id}_")
        
        # 필요한 하위 디렉터리 생성
        os.makedirs(f"{workspace}/output", exist_ok=True)
        os.makedirs(f"{workspace}/output/log", exist_ok=True)
        os.makedirs(f"{workspace}/output/audio", exist_ok=True)
        
        # 소스 비디오 다운로드
        await DubbingService._download_source_video(job, workspace)
        
        # 커스텀 용어 파일 복사 (존재하는 경우)
        await DubbingService._copy_custom_terms(workspace)
        
        return workspace

    @staticmethod
    async def _download_source_video(job: Job, workspace: str) -> None:
        """소스 비디오 다운로드"""
        try:
            # Video 정보 조회
            from app.core.database import get_async_session
            from sqlalchemy import select
            
            async for db in get_async_session():
                result = await db.execute(select(Video).where(Video.id == job.video_id))
                video = result.scalar_one_or_none()
                break
            
            if not video or not video.file_path:
                raise Exception("소스 비디오를 찾을 수 없습니다.")
            
            # S3에서 비디오 다운로드
            video_content = await storage_service.download_file(video.file_path)
            
            # 로컬에 저장 (AI 모듈들이 찾을 수 있도록)
            video_filename = f"source_video{Path(video.file_path).suffix}"
            local_video_path = f"{workspace}/{video_filename}"
            
            with open(local_video_path, 'wb') as f:
                f.write(video_content)
                
        except Exception as e:
            raise Exception(f"소스 비디오 다운로드 실패: {str(e)}")

    @staticmethod
    async def _copy_custom_terms(workspace: str) -> None:
        """커스텀 용어 파일 복사"""
        try:
            # 프로젝트 루트의 custom_terms.xlsx 복사
            root_custom_terms = "custom_terms.xlsx"
            workspace_custom_terms = f"{workspace}/custom_terms.xlsx"
            
            if os.path.exists(root_custom_terms):
                shutil.copy2(root_custom_terms, workspace_custom_terms)
                
        except Exception:
            # 커스텀 용어 파일이 없어도 계속 진행
            pass

    @staticmethod
    async def _prepare_ai_config(job: Job) -> None:
        """AI 모듈 설정 준비"""
        try:
            # AI 설정 모듈 동적 import
            config_utils = importlib.import_module("ai.utils.config_utils")
            update_key = config_utils.update_key
            load_key = config_utils.load_key
            
            # Job 설정에서 AI 설정 업데이트
            job_config = job.job_config or {}
            
            # config.yaml의 기존 값을 읽어와서 job_config에서 지정된 값만 덮어쓰기
            
            # 언어 설정 (job_config > config.yaml)
            target_language = job_config.get("target_language") or load_key("target_language")
            # 언어 코드 정규화 (kr -> ko 등)
            language_mapping = {"kr": "ko", "cn": "zh", "jp": "ja"}
            target_language = language_mapping.get(target_language, target_language)
            update_key("target_language", target_language)
            
            # TTS 방법 설정 (job_config > config.yaml)
            tts_method = job_config.get("tts_method") or load_key("tts_method")
            update_key("tts_method", tts_method)
            
            # 음성 ID 설정 (TTS 방법에 따라 다름)
            if "voice_id" in job_config:
                voice_id = job_config["voice_id"]
                
                # TTS 방법별로 적절한 키에 설정
                if tts_method == "openai_tts":
                    update_key("openai_tts.voice", voice_id)
                elif tts_method == "azure_tts":
                    update_key("azure_tts.voice", voice_id)
                elif tts_method == "edge_tts":
                    update_key("edge_tts.voice", voice_id)
                elif tts_method == "sf_fish_tts":
                    update_key("sf_fish_tts.voice", voice_id)
                elif tts_method == "fish_tts":
                    update_key("fish_tts.character", voice_id)
                elif tts_method == "gpt_sovits":
                    update_key("gpt_sovits.character", voice_id)
                
            # 배경음악 보존 설정 (job_config > config.yaml)
            preserve_bg = job_config.get("preserve_background_music")
            if preserve_bg is not None:
                update_key("demucs", preserve_bg)
            
            # Whisper 설정
            update_key("whisper.language", target_language)
            # detected_language도 설정 (일부 AI 모듈에서 사용)
            update_key("whisper.detected_language", target_language)
            
            # API 키 설정 (환경변수나 settings에서 가져와야 할 수도 있음)
            # 현재는 config.yaml의 기본값 사용
            
            # 더빙 품질 관련 설정들 (config.yaml 기본값 사용)
            # - speed_factor (오디오 속도 조절)
            # - subtitle 관련 설정들
            # - tolerance 관련 설정들
            
            # 더빙 작업에 필수적인 설정들 확인 및 강제 적용
            try:
                subtitle_burn = load_key("burn_subtitles")
                if not subtitle_burn:
                    update_key("burn_subtitles", True)  # 더빙에는 자막 번인 필수
            except KeyError:
                update_key("burn_subtitles", True)
                
            # 안전한 기본값들 설정 (config.yaml에 없는 경우)
            try:
                load_key("max_workers")
            except KeyError:
                update_key("max_workers", 2)  # 안전한 기본값
                
            try:
                load_key("ffmpeg_gpu")
            except KeyError:
                update_key("ffmpeg_gpu", False)  # 호환성을 위해 비활성화
                
        except Exception as e:
            raise Exception(f"AI 설정 준비 실패: {str(e)}")

    @staticmethod
    async def _create_job_steps(db: AsyncSession, job_id: str) -> None:
        """Job Steps 생성"""
        steps_data = [
            {"name": step["name"]} for step in DubbingService.DUBBING_STEPS
        ]
        await JobService.create_job_steps(db, job_id, steps_data)

    @staticmethod
    async def _execute_step(
        db: AsyncSession, 
        job_id: str, 
        step_config: Dict[str, Any],
        workspace: str
    ) -> None:
        """개별 파이프라인 단계 실행"""
        step_name = step_config["name"]
        
        try:
            # 단계 시작
            await JobService.update_step_status(
                db, job_id, step_name, "processing", 0.0
            )
            
            # AI 모듈 실행
            await DubbingService._run_ai_module(step_config)
            
            # 단계 완료
            await JobService.update_step_status(
                db, job_id, step_name, "completed", 100.0
            )
            
            # 전체 진행률 업데이트
            await DubbingService._update_overall_progress(db, job_id)
            
        except Exception as e:
            # 단계 실패
            await JobService.update_step_status(
                db, job_id, step_name, "failed", 0.0,
                error_message=str(e)
            )
            raise Exception(f"{step_name} 단계 실패: {str(e)}")

    @staticmethod
    async def _run_ai_module(step_config: Dict[str, Any]) -> None:
        """AI 모듈 실행"""
        try:
            # 동적 모듈 import
            module = importlib.import_module(step_config["module"])
            function = getattr(module, step_config["function"])
            
            # 비동기 함수인지 확인 후 실행
            if asyncio.iscoroutinefunction(function):
                await function()
            else:
                # 동기 함수는 스레드에서 실행
                await asyncio.to_thread(function)
                
        except Exception as e:
            raise Exception(f"AI 모듈 실행 실패 ({step_config['module']}.{step_config['function']}): {str(e)}")

    @staticmethod
    async def _update_overall_progress(db: AsyncSession, job_id: str) -> None:
        """전체 진행률 업데이트"""
        try:
            # 모든 단계의 가중치 합계
            total_weight = sum(step["weight"] for step in DubbingService.DUBBING_STEPS)
            
            # 완료된 단계들의 가중치 합계
            from sqlalchemy import select
            from app.models.job import JobStep
            
            result = await db.execute(
                select(JobStep).where(JobStep.job_id == job_id)
            )
            steps = result.scalars().all()
            
            completed_weight = 0
            for step in steps:
                if step.status == "completed":
                    step_config = next(
                        (s for s in DubbingService.DUBBING_STEPS if s["name"] == step.step_name),
                        None
                    )
                    if step_config:
                        completed_weight += step_config["weight"]
            
            # 전체 진행률 계산
            overall_progress = (completed_weight / total_weight) * 100
            
            # Job 진행률 업데이트
            await JobService.update_job_progress(db, job_id, overall_progress)
            
        except Exception:
            # 진행률 업데이트 실패해도 파이프라인은 계속
            pass

    @staticmethod
    async def _finalize_dubbing(db: AsyncSession, job: Job, workspace: str) -> None:
        """더빙 완료 처리"""
        try:
            # 결과 파일들 S3 업로드
            result_files = await DubbingService._upload_result_files(job, workspace)
            
            # Job 결과 데이터 설정
            result_data = {
                "dubbed_video_url": result_files.get("dubbed_video"),
                "subtitles_url": result_files.get("subtitles"),
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Job 완료
            await JobService.complete_job(db, job.id, result_data)
            
            # Video 상태 업데이트
            await DubbingService._update_video_status(db, job, result_files)
            
            # 영상 처리 완료 알림 발송
            try:
                # 비디오 정보 조회
                from sqlalchemy import select
                video_result = await db.execute(select(Video).where(Video.id == job.video_id))
                video = video_result.scalar_one_or_none()
                
                # 사용자 정보 조회
                user_result = await db.execute(select(User).where(User.id == job.user_id))
                user = user_result.scalar_one_or_none()
                
                if video and user:
                    # 처리 시간 계산
                    processing_duration = "알 수 없음"
                    if job.started_at and job.completed_at:
                        duration_seconds = (job.completed_at - job.started_at).total_seconds()
                        hours = int(duration_seconds // 3600)
                        minutes = int((duration_seconds % 3600) // 60)
                        if hours > 0:
                            processing_duration = f"{hours}시간 {minutes}분"
                        else:
                            processing_duration = f"{minutes}분"
                    
                    # 언어 이름 변환
                    target_language = job.job_config.get("target_language", "ko")
                    language_names = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어", "es": "스페인어", "fr": "프랑스어"}
                    target_language_name = language_names.get(target_language, target_language)
                    
                    # 다운로드 URL (프론트엔드에서 처리)
                    download_url = f"{settings.FRONTEND_URL}/videos/{video.id}/download"
                    
                    await NotificationService.send_video_processing_complete_notification(
                        user=user,
                        video_title=video.title,
                        target_language=target_language_name,
                        processing_duration=processing_duration,
                        download_url=download_url
                    )
            except Exception as e:
                # 알림 발송 실패해도 더빙 완료는 성공으로 처리
                print(f"영상 처리 완료 알림 발송 실패: {str(e)}")
            
        except Exception as e:
            raise Exception(f"더빙 완료 처리 실패: {str(e)}")

    @staticmethod
    async def _upload_result_files(job: Job, workspace: str) -> Dict[str, str]:
        """결과 파일들 S3 업로드"""
        result_files = {}
        
        try:
            # 더빙된 비디오 업로드
            dubbed_video_path = f"{workspace}/output/output_dub.mp4"
            if os.path.exists(dubbed_video_path):
                video_key = storage_service.generate_file_key(
                    job.user_id, "video", f"dubbed_{job.video_id}.mp4"
                )
                
                with open(dubbed_video_path, 'rb') as f:
                    video_content = f.read()
                
                # UploadFile 객체 생성 (storage_service.upload_file 호환)
                class FakeUploadFile:
                    def __init__(self, content, filename):
                        self.file = type('obj', (object,), {'read': lambda: content})()
                        self.filename = filename
                        self.content_type = "video/mp4"
                
                fake_file = FakeUploadFile(video_content, f"dubbed_{job.video_id}.mp4")
                video_url = await storage_service.upload_file(fake_file, video_key)
                result_files["dubbed_video"] = video_url
            
            # 자막 파일 업로드
            subtitle_path = f"{workspace}/output/dub.srt"
            if os.path.exists(subtitle_path):
                subtitle_key = storage_service.generate_file_key(
                    job.user_id, "subtitle", f"dubbed_{job.video_id}.srt"
                )
                
                with open(subtitle_path, 'rb') as f:
                    subtitle_content = f.read()
                
                fake_srt_file = FakeUploadFile(subtitle_content, f"dubbed_{job.video_id}.srt")
                subtitle_url = await storage_service.upload_file(fake_srt_file, subtitle_key)
                result_files["subtitles"] = subtitle_url
            
            return result_files
            
        except Exception as e:
            raise Exception(f"결과 파일 업로드 실패: {str(e)}")

    @staticmethod
    async def _update_video_status(db: AsyncSession, job: Job, result_files: Dict[str, str]) -> None:
        """비디오 상태 업데이트"""
        try:
            from sqlalchemy import select, update
            from app.models.video import Video
            
            # Video 업데이트
            await db.execute(
                update(Video)
                .where(Video.id == job.video_id)
                .values(
                    status="completed",
                    dubbed_file_path=result_files.get("dubbed_video"),
                    subtitle_file_path=result_files.get("subtitles"),
                    processing_completed_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await db.commit()
            
        except Exception as e:
            # 비디오 상태 업데이트 실패해도 Job은 완료된 것으로 처리
            print(f"비디오 상태 업데이트 실패: {str(e)}")

    @staticmethod
    async def cancel_dubbing_job(db: AsyncSession, job_id: str, user_id: str) -> bool:
        """더빙 작업 취소"""
        try:
            # Job 취소
            success = await JobService.cancel_job(db, job_id, user_id)
            
            if success:
                # 관련 임시 파일들 정리 (백그라운드에서)
                asyncio.create_task(DubbingService._cleanup_job_files(job_id))
            
            return success
            
        except Exception:
            return False

    @staticmethod
    async def _cleanup_job_files(job_id: str) -> None:
        """작업 파일들 정리"""
        try:
            # 임시 디렉터리 패턴으로 찾아서 삭제
            temp_dir = tempfile.gettempdir()
            for item in os.listdir(temp_dir):
                if item.startswith(f"dubbing_{job_id}_"):
                    full_path = os.path.join(temp_dir, item)
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path, ignore_errors=True)
                        
        except Exception:
            # 정리 실패해도 무시
            pass