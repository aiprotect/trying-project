from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

class AuthEmailService:
    @staticmethod
    def send_password_reset_email(user, request):
        """
        ارسال ایمیل بازیابی رمز عبور با ویژگی‌های امنیتی
        """
        # تولید کد یکتا برای بازیابی رمز
        reset_code = get_random_string(72)
        user.email_active_code = reset_code
        user.save()

        # ساخت لینک بازیابی
        reset_link = request.build_absolute_uri(
            f"/reset-password/{reset_code}/"
        )

        # اطلاعات ایمیل
        subject = "بازیابی رمز عبور"
        context = {
            'user': user,
            'reset_link': reset_link,
            'expiration_hours': 24,  # مدت اعتبار لینک
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT')[:200],
        }

        # رندر محتوای ایمیل
        html_message = render_to_string('account_module/reset_password.html', context)
        plain_message = strip_tags(html_message)

        # ارسال ایمیل
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,  # از EMAIL_FROM_ADDRESS در تنظیمات استفاده می‌کند
            to=[user.email],
            headers={
                'X-Priority': '1',  # اهمیت بالا
            }
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        # لاگ کردن عملیات (اختیاری)
        # logger.info(f"Password reset email sent to {user.email} from IP: {context['ip_address']}")