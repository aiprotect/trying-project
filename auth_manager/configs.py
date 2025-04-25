class AuthConfig:
    # تنظیمات ظاهری
    LOGIN_REDIRECT_URL = 'profile'
    REGISTER_REDIRECT_URL = 'activation_sent'
    ACTIVATION_EXPIRE_DAYS = 1
    
    # استایل‌های پیش‌فرض
    FORM_STYLES = {
        'input_class': 'form-control',
        'label_class': 'form-label',
        'error_class': 'text-danger',
        'submit_class': 'btn btn-primary'
    }
    
    # متن‌های پیش‌فرض
    MESSAGES = {
        'activation_sent': 'لینک فعال‌سازی به ایمیل شما ارسال شد',
        'activation_failed': 'لینک فعال‌سازی نامعتبر یا منقضی شده است',
        'login_success': 'ورود با موفقیت انجام شد'
    }