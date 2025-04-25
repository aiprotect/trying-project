from django.db import models

# Create your models here.

class ContactUs(models.Model):
    subject =  models.CharField(max_length=255,verbose_name='عنوان')
    full_name = models.CharField(max_length=200,verbose_name='نام و نام کاربری')
    email = models.EmailField(max_length=300,verbose_name='ایمیل')
    message = models.TextField(verbose_name='متن پیغام')
    is_read_by_admin = models.BooleanField(default=False, verbose_name='خوانده شده توسط ادمین')
    data_request = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت',null=True)
    responce = models.TextField(verbose_name='پاسخ ادمین',null=True,blank=True)
    image = models.ImageField(upload_to='contact-us/images',null=True,blank=True)

    def __str__(self):
        return self.subject
    
    class Meta:
        verbose_name_plural = 'لیست تماس با ما'

