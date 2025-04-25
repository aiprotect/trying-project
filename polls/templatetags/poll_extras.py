# myapp/templatetags/product_filters.py
from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='three_digits_currency')
def three_digits_currency(value, currency=None):
    """
    تبدیل عدد به فرمت مالی با جداکننده هزارگان
    مقدار پیش‌فرض ارز از تنظیمات سایت گرفته می‌شود
    مثال: 
    ورودی: 123456789
    خروجی: "123,456,789 تومان"
    """
    try:
        value = int(value)
        currency = currency or getattr(settings, 'DEFAULT_CURRENCY', 'تومان')
        return "{:,} {}".format(value, currency)
    except (ValueError, TypeError):
        return str(value) if value is not None else "0"

@register.filter(name='round_price')
def round_price(value):
    """
    نمایش قیمت بدون واحد پولی و فقط با ارقام اصلی
    مثال:
    ورودی: 123456789
    خروجی: "123456789"
    """
    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value) if value is not None else "0"

@register.filter(name='get_range')
def get_range(value):
    """
    ایجاد یک رنج از اعداد برای استفاده در حلقه‌های تمپلیت
    مثال:
    ورودی: 5
    خروجی: range(1, 6) => [1, 2, 3, 4, 5]
    """
    try:
        value = int(float(value))
        return range(1, value + 1) if value > 0 else range(0)
    except (ValueError, TypeError):
        return range(0)
    
@register.filter
def get_range(value):
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)