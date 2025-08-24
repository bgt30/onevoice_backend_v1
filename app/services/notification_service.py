# 이메일 알림 서비스 - 회원가입 인증, 비밀번호 초기화, 영상 처리 알림
import asyncio
from typing import Optional, Dict, Any
from jinja2 import Environment, BaseLoader
import boto3
from botocore.exceptions import ClientError

from app.models.user import User
from app.config import get_settings

settings = get_settings()


class NotificationService:
    """이메일 알림 서비스 - 3가지 핵심 이메일 발송 전용"""

    # 알림 템플릿 정의
    TEMPLATES = {
        "signup_verification": {
            "title": "회원가입 인증",
            "message": "OneVoice 회원가입을 완료하려면 이메일 인증을 해주세요.",
            "email_subject": "OneVoice - 이메일 인증이 필요합니다",
            "email_template": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; }
        .button { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 OneVoice</h1>
        </div>
        <div class="content">
            <h2>환영합니다!</h2>
            <p>안녕하세요 <strong>{{user_name}}</strong>님,</p>
            <p>OneVoice에 가입해주셔서 감사합니다! 계정을 활성화하려면 아래 버튼을 클릭해주세요.</p>
            <a href="{{verification_url}}" class="button">이메일 인증하기</a>
            <p>또는 다음 링크를 복사해서 브라우저에 붙여넣으세요:</p>
            <p style="word-break: break-all; background: #f8f9fa; padding: 10px;">{{verification_url}}</p>
            <p><small>이 링크는 24시간 후 만료됩니다.</small></p>
        </div>
        <div class="footer">
            <p>OneVoice - AI 기반 다국어 음성 더빙 서비스</p>
        </div>
    </div>
</body>
</html>
            """
        },
        "password_reset": {
            "title": "비밀번호 재설정",
            "message": "비밀번호 재설정 링크를 발송했습니다.",
            "email_subject": "OneVoice - 비밀번호 재설정",
            "email_template": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
        .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; }
        .button { background: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 OneVoice</h1>
        </div>
        <div class="content">
            <h2>비밀번호 재설정</h2>
            <p>안녕하세요 <strong>{{user_name}}</strong>님,</p>
            <p>비밀번호 재설정을 요청하셨습니다. 아래 버튼을 클릭하여 새로운 비밀번호를 설정해주세요.</p>
            <a href="{{reset_url}}" class="button">비밀번호 재설정</a>
            <p>또는 다음 링크를 복사해서 브라우저에 붙여넣으세요:</p>
            <p style="word-break: break-all; background: #f8f9fa; padding: 10px;">{{reset_url}}</p>
            <p><small>이 링크는 1시간 후 만료됩니다.</small></p>
            <p><small>만약 비밀번호 재설정을 요청하지 않았다면 이 이메일을 무시해주세요.</small></p>
        </div>
        <div class="footer">
            <p>OneVoice - AI 기반 다국어 음성 더빙 서비스</p>
        </div>
    </div>
</body>
</html>
            """
        },
        "video_processing_complete": {
            "title": "영상 처리 완료",
            "message": "'{video_title}' 더빙 작업이 완료되었습니다!",
            "email_subject": "OneVoice - 더빙 작업 완료",
            "email_template": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
        .header { background: #28a745; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; }
        .button { background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 OneVoice</h1>
        </div>
        <div class="content">
            <div class="success">
                <h2>더빙 작업이 완료되었습니다!</h2>
            </div>
            <p>안녕하세요 <strong>{{user_name}}</strong>님,</p>
            <p><strong>'{{video_title}}'</strong> 더빙 작업이 성공적으로 완료되었습니다.</p>
            <p>처리 시간: {{processing_duration}}</p>
            <p>타겟 언어: {{target_language}}</p>
            <a href="{{download_url}}" class="button">결과 다운로드</a>
            <p>더빙된 영상과 자막 파일을 다운로드하실 수 있습니다.</p>
        </div>
        <div class="footer">
            <p>OneVoice - AI 기반 다국어 음성 더빙 서비스</p>
        </div>
    </div>
</body>
</html>
            """
        },
        "video_processing_failed": {
            "title": "영상 처리 실패",
            "message": "'{video_title}' 더빙 작업 중 오류가 발생했습니다.",
            "email_subject": "OneVoice - 더빙 작업 실패",
            "email_template": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
        .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; }
        .button { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ OneVoice</h1>
        </div>
        <div class="content">
            <div class="error">
                <h2>더빙 작업이 실패했습니다</h2>
            </div>
            <p>안녕하세요 <strong>{{user_name}}</strong>님,</p>
            <p><strong>'{{video_title}}'</strong> 더빙 작업 중 오류가 발생했습니다.</p>
            <p><strong>오류 내용:</strong> {{error_message}}</p>
            <p>사용된 크레딧은 자동으로 환불되었습니다. 다시 시도해보시거나 고객지원팀에 문의해주세요.</p>
            <a href="{{retry_url}}" class="button">다시 시도하기</a>
        </div>
        <div class="footer">
            <p>OneVoice - AI 기반 다국어 음성 더빙 서비스</p>
            <p>문의: support@onevoice.ai</p>
        </div>
    </div>
</body>
</html>
            """
        }
    }



    @staticmethod
    async def send_signup_verification_email(
        user: User,
        verification_token: str
    ) -> bool:
        """회원가입 인증 이메일 발송"""
        try:
            template = NotificationService.TEMPLATES["signup_verification"]
            
            # 인증 URL 생성
            verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"
            
            # 템플릿 데이터
            template_data = {
                "user_name": user.username or user.email,
                "verification_url": verification_url
            }
            
            # 이메일 발송
            return await NotificationService._send_email(
                to_email=user.email,
                subject=template["email_subject"],
                html_content=NotificationService._render_template(
                    template["email_template"], 
                    template_data
                )
            )
            
        except Exception as e:
            print(f"회원가입 인증 이메일 발송 실패: {str(e)}")
            return False

    @staticmethod
    async def send_password_reset_email(
        user: User,
        reset_token: str
    ) -> bool:
        """비밀번호 재설정 이메일 발송"""
        try:
            template = NotificationService.TEMPLATES["password_reset"]
            
            # 재설정 URL 생성
            reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
            
            # 템플릿 데이터
            template_data = {
                "user_name": user.username or user.email,
                "reset_url": reset_url
            }
            
            # 이메일 발송
            return await NotificationService._send_email(
                to_email=user.email,
                subject=template["email_subject"],
                html_content=NotificationService._render_template(
                    template["email_template"], 
                    template_data
                )
            )
            
        except Exception as e:
            print(f"비밀번호 재설정 이메일 발송 실패: {str(e)}")
            return False

    @staticmethod
    async def send_video_processing_complete_notification(
        user: User,
        video_title: str,
        target_language: str,
        processing_duration: str,
        download_url: str
    ) -> bool:
        """영상 처리 완료 알림 발송"""
        try:
            # 이메일 알림이 비활성화된 경우 스킵
            if not user.email_notifications:
                return True
            
            template = NotificationService.TEMPLATES["video_processing_complete"]
            
            # 템플릿 데이터
            template_data = {
                "user_name": user.username or user.email,
                "video_title": video_title,
                "target_language": target_language,
                "processing_duration": processing_duration,
                "download_url": download_url
            }
            
            # 이메일 발송
            return await NotificationService._send_email(
                to_email=user.email,
                subject=template["email_subject"],
                html_content=NotificationService._render_template(
                    template["email_template"], 
                    template_data
                )
            )
            
        except Exception as e:
            print(f"영상 처리 완료 알림 발송 실패: {str(e)}")
            return False

    @staticmethod
    async def send_video_processing_failed_notification(
        user: User,
        video_title: str,
        error_message: str,
        retry_url: Optional[str] = None
    ) -> bool:
        """영상 처리 실패 알림 발송"""
        try:
            # 이메일 알림이 비활성화된 경우 스킵
            if not user.email_notifications:
                return True
            
            template = NotificationService.TEMPLATES["video_processing_failed"]
            
            # 템플릿 데이터
            template_data = {
                "user_name": user.username or user.email,
                "video_title": video_title,
                "error_message": error_message,
                "retry_url": retry_url or f"{settings.FRONTEND_URL}/videos"
            }
            
            # 이메일 발송
            return await NotificationService._send_email(
                to_email=user.email,
                subject=template["email_subject"],
                html_content=NotificationService._render_template(
                    template["email_template"], 
                    template_data
                )
            )
            
        except Exception as e:
            print(f"영상 처리 실패 알림 발송 실패: {str(e)}")
            return False



    @staticmethod
    async def _send_email(
        to_email: str,
        subject: str,
        html_content: str
    ) -> bool:
        """이메일 발송 (SES)"""
        if not settings.SES_ENABLED:
            print("SES 비활성화: 이메일 발송 스킵")
            return True

        try:
            ses_client = boto3.client('ses', region_name=settings.AWS_REGION)
            await asyncio.to_thread(
                ses_client.send_email,
                Source=f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_content, 'Charset': 'UTF-8'}
                    }
                }
            )
            return True
        except ClientError as e:
            print(f"SES 이메일 발송 실패: {str(e)}")
            return False

    @staticmethod
    async def publish_alert(subject: str, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """운영 알림을 SNS로 발행"""
        if not settings.SNS_ALERTS_TOPIC_ARN:
            return False
        try:
            sns = boto3.client('sns', region_name=settings.AWS_REGION)
            payload = message
            if context:
                try:
                    import json as _json
                    payload = f"{message}\nContext: {_json.dumps(context)[:2000]}"
                except Exception:
                    pass
            await asyncio.to_thread(
                sns.publish,
                TopicArn=settings.SNS_ALERTS_TOPIC_ARN,
                Subject=subject,
                Message=payload,
            )
            return True
        except ClientError:
            return False

    # Pipeline convenience wrappers
    async def send_job_completion_notification(self, job_id: str) -> bool:
        try:
            from app.core.database import get_async_session
            from app.services.job_service import JobService
            async with get_async_session() as db:
                job = await JobService.get_job(db, job_id)
                if not job or not job.video:
                    return False
                user = getattr(job.video, 'user', None)
                if not user:
                    from sqlalchemy import select as _select
                    from app.models.user import User as _User
                    res = await db.execute(_select(_User).where(_User.id == job.user_id))
                    user = res.scalar_one_or_none()
                processing_duration = "-"
                if job.started_at and job.completed_at:
                    delta = job.completed_at - job.started_at
                    processing_duration = str(delta)
                download_url = f"{settings.FRONTEND_URL}/videos/{job.video_id}"
                return await NotificationService.send_video_processing_complete_notification(
                    user=user,
                    video_title=job.video.title if job.video else "",
                    target_language=getattr(job, 'target_language', None) or job.job_config.get('target_language', ''),
                    processing_duration=processing_duration,
                    download_url=download_url,
                )
        except Exception:
            return False

    async def send_job_error_notification(self, job_id: str, step_name: str, error_message: str) -> bool:
        try:
            from app.core.database import get_async_session
            from app.services.job_service import JobService
            async with get_async_session() as db:
                job = await JobService.get_job(db, job_id)
                if not job or not job.video:
                    return False
                user = getattr(job.video, 'user', None)
                if not user:
                    from sqlalchemy import select as _select
                    from app.models.user import User as _User
                    res = await db.execute(_select(_User).where(_User.id == job.user_id))
                    user = res.scalar_one_or_none()
                retry_url = f"{settings.FRONTEND_URL}/videos/{job.video_id}"
                await NotificationService.publish_alert(
                    subject="Dubbing pipeline failed",
                    message=f"Job {job_id} failed at step {step_name}: {error_message}",
                    context={"job_id": job_id, "step": step_name}
                )
                return await NotificationService.send_video_processing_failed_notification(
                    user=user,
                    video_title=job.video.title if job.video else "",
                    error_message=error_message,
                    retry_url=retry_url,
                )
        except Exception:
            return False

    async def send_job_cancellation_notification(self, job_id: str) -> bool:
        try:
            await NotificationService.publish_alert(
                subject="Dubbing job cancelled",
                message=f"Job {job_id} was cancelled",
                context={"job_id": job_id}
            )
        except Exception:
            pass
        return True

    @staticmethod
    def _render_template(template: str, data: Dict[str, Any]) -> str:
        """템플릿 렌더링"""
        try:
            env = Environment(loader=BaseLoader())
            template_obj = env.from_string(template)
            return template_obj.render(**data)
            
        except Exception as e:
            print(f"템플릿 렌더링 실패: {str(e)}")
            return template  # 렌더링 실패 시 원본 반환