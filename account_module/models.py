from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import EmailValidator
from django.utils import timezone
from datetime import timedelta
from django_q.tasks import schedule
from django_q.models import Schedule
from django_jalali.db import models as jmodels
from persiantools.jdatetime import JalaliDate
from django.core.exceptions import ValidationError
from django_jalali.db import models as jmodels
from django.core.validators import RegexValidator
from django_jalali import forms as jforms
from django.utils.translation import gettext_lazy as _

# در product_module/models.py


class User(AbstractUser):

    email = models.EmailField(
        unique=True,
        verbose_name='ایمیل کاربر',
        validators=[EmailValidator(message="لطفاً یک ایمیل معتبر وارد کنید")]
    )
    email_active_code = models.CharField(
        max_length=102,
        verbose_name='کد فعالسازی حساب',
        blank=True,
        null=True,
        unique=True
    )
    reset_code_expiration = models.DateTimeField(
        null=True,
        blank=True
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name='نام کامل',
        blank=True
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        verbose_name='تصویر پروفایل'
    )
    phone_number = models.CharField(  # اضافه کردن فیلد شماره تلفن برای احراز دو مرحله‌ای
        max_length=15,
        blank=True,
        null=True,
        verbose_name='شماره تلفن'
    )
    is_verified_phone = models.BooleanField(
        default=False,
        verbose_name='تلفن تأیید شده'
    )
    favorite_products = models.ManyToManyField(
        'product_module.Product',
        verbose_name='محصولات مورد علاقه',
        related_name='users_who_favorited'  # تغییر related_name به یک نام منحصر به فرد
    )
    account_suspension = models.BooleanField(
        default=False,
        verbose_name='تعلیق کردن حساب کاربر',
        help_text='درصورت فعال بودن کاربر نمیتواند به سایت دسترسی داشته باشد '
    )

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)



class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', _('مرد')),
        ('F', _('زن')),
        ('O', _('سایر')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('کاربر')
    )
    
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاریخ تولد'),
    )
    
    national_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_('کد ملی'),
        validators=[
            RegexValidator(
                regex='^[0-9]{10}$',
                message=_('کد ملی باید ۱۰ رقم باشد')
            )
        ]
    )
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name=_('جنسیت')
    )
    
    phone_number = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        verbose_name=_('تلفن همراه'),
        validators=[
            RegexValidator(
                regex='^09[0-9]{9}$',
                message=_('شماره تلفن باید با 09 شروع شود')
            )
        ]
    
    )

    address = models.CharField(
        max_length = 150,
        null = True,
        blank = True,
        verbose_name = 'آدرس محل زندگی'
    )
    city = models.CharField(
        max_length = 80,
        null = True,
        blank = True,
        verbose_name = 'شهر سکونت'
    )
    

    class Meta:
        verbose_name = _('پروفایل کاربر')
        verbose_name_plural = _('پروفایل‌های کاربران')
        ordering = ['-id']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - پروفایل"

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = JalaliDate.today()
        birth = JalaliDate(self.birth_date)
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        return age

    @property
    def formatted_birth_date(self):
        if self.birth_date:
            return JalaliDate(self.birth_date).strftime("%Y/%m/%d")
        return None

class UserActivity(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='activity'
    )
    last_activity = models.DateTimeField(default=timezone.now)

    @property
    def is_online(self):
        return (timezone.now() - self.last_activity) < timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.username}'s activity"


class ContactUsSupendedModel(models.Model):
    subject =  models.CharField(max_length=255,verbose_name='عنوان')
    full_name = models.CharField(max_length=200,verbose_name='نام و نام کاربری')
    email = models.EmailField(max_length=300,verbose_name='ایمیل')
    message = models.TextField(verbose_name='متن پیغام')
    is_read_by_admin = models.BooleanField(default=False, verbose_name='خوانده شده توسط ادمین')
    data_request = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت',null=True)
    responce = models.TextField(verbose_name='پاسخ ادمین',null=True,blank=True)


    def __str__(self):
        return self.subject
    
    class Meta:
        verbose_name_plural = 'لیست تماس با ما'


class AboutUsModel(models.Model):
        fax = models.IntegerField(
            null = False,
            blank = False,
            verbose_name = 'فکس'
        )
        email = models.EmailField(
            null= False,
            blank = False,
            verbose_name = 'ایمیل پشتیبانی'
        )
        is_active = models.BooleanField(
            default = True,
            verbose_name = 'نمایش این جزییات'
        )

        def __str__(self):
            return self.email
        
        class Meta:
            verbose_name = 'اطلاعات صفحه تماس با ما'
            verbose_name_plural = 'اطلاعات صفحه تماس با ما'