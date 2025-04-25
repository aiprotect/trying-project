
from django.apps import AppConfig

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account_module'
    verbose_name = 'حساب‌های کاربری'

    def ready(self):
        # ثبت سیگنال‌ها
        import account_module.signals