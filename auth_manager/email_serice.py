from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string
from django.conf import settings
import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class AuthEmailService:

    @classmethod
    def _send_email(cls, subject, template, context, recipient):
        """متد پایه برای ارسال ایمیل"""
        try:
            html_message = render_to_string(template, context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                headers={'X-Priority': '1'}
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            logger.info(f"Email sent to {recipient} with subject: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    @classmethod
    def send_activation_email(cls, user, request):
        """ارسال ایمیل فعال‌سازی حساب"""
        if not user.email:
            logger.warning(f"User {user.username} has no email for activation")
            return False

        user.email_active_code = get_random_string(72)
        user.email_active_code_expires = timezone.now() + timedelta(hours=24)
        user.save()

        return cls._send_email(
            subject="فعال‌سازی حساب کاربری",
            template='account_module/activation_email.html',
            context={
                'user': user,
                'activation_link': request.build_absolute_uri(
                    f"/activate/{user.email_active_code}/"
                ),
                'expiration_hours': 24
            },
            recipient=user.email
        )

    @classmethod
    def send_password_reset_email(cls, user, request):
        """ارسال ایمیل بازیابی رمز عبور"""
        if not user.email:
            logger.warning(f"User {user.username} has no email for password reset")
            return False

        reset_code = get_random_string(72)
        user.email_active_code = reset_code
        user.email_active_code_expires = timezone.now() + timedelta(hours=24)
        user.save()

        return cls._send_email(
            subject="بازیابی رمز عبور",
            template='account_module/password_reset_email.html',
            context={
                'user': user,
                'reset_link': request.build_absolute_uri(
                    f"/reset-pass/{reset_code}/"
                ),
                'expiration_hours': 24,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')[:200],
            },
            recipient=user.email
        )

    @staticmethod
    def message_welcome_login(user, request):
        user_agent = request.META.get('HTTP_USER_AGENT', 'نامشخص')

        subject = "ورود جدید به حساب کاربری"
        context = {
            'user': user,
            'user_agent': user_agent,  # اضافه کردن user_agent به context
            'ip_address': request.META.get('REMOTE_ADDR', 'نامشخص'),
            'login_time': timezone.now()
        }

        html_message = render_to_string('account_module/welcome_login_page.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()