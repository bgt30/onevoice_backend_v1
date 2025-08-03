# 이메일 알림 서비스 - 회원가입 인증, 비밀번호 초기화, 영상 처리 알림
import asyncio
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional, Dict, Any
from jinja2 import Environment, BaseLoader

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
        """이메일 발송 (SMTP)"""
        try:
            # SMTP 설정이 없으면 스킵
            if not all([
                settings.SMTP_HOST,
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
            ]):
                print("SMTP 설정이 없어 이메일 발송을 건너뜁니다.")
                return True  # 개발환경에서는 성공으로 처리
            
            # 이메일 메시지 생성
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg['To'] = to_email
            
            # HTML 파트 추가
            html_part = MimeText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 발송
            await asyncio.to_thread(NotificationService._send_smtp_email, msg)
            
            return True
            
        except Exception as e:
            print(f"이메일 발송 실패: {str(e)}")
            return False

    @staticmethod
    def _send_smtp_email(msg: MimeMultipart) -> None:
        """동기 SMTP 이메일 발송"""
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)

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