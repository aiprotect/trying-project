from django.db import models
from datetime import datetime

# Create your models here.
class AboutUsModel(models.Model):
    email = models.EmailField(verbose_name='ایمیل ما')
    image_us = models.ImageField(upload_to='about_us/images/', verbose_name='تصویر ما',null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name='شماره تماس ما')
    fax = models.BigIntegerField( verbose_name='فکس',null=True, blank=True)
    address = models.TextField(verbose_name='ادرس ما')
    facebook = models.URLField(verbose_name='ادرس فیسبوک', null=True, blank=True)
    instagram = models.URLField(verbose_name='ادرس اینستاگرام', null=True, blank=True)
    whatsapp = models.URLField(verbose_name='ادرس واتساپ', null=True, blank=True)
    telegram = models.URLField(verbose_name='ادرس تلگرام', null=True, blank=True)
    twitter = models.URLField(verbose_name='ادرس توییتر', null=True, blank=True)
    youtube = models.URLField(verbose_name='ادرس چنل یوتیوب', null=True, blank=True)
    city = models.CharField(max_length=100,verbose_name='شهر')
    text_about_us = models.TextField(verbose_name='متن درباره ما',null=True, blank=True)
    number_year_old = models.IntegerField(null=True,blank=True,verbose_name='سال تجربه')
    is_active_view = models.BooleanField(default=True, verbose_name='نمایش جزیات تماس با ما')
    last_updated_month = models.IntegerField(null=True, blank=True)


    def save(self, *args, **kwargs):
        current_month = datetime.now().month

        # اگر رکورد جدید است یا ماه تغییر کرده است
        if self.pk is None or (self.last_updated_month and self.last_updated_month != current_month):
            if self.number_year_old is None:
                self.number_year_old = 1
            else:
                self.number_year_old += 1
            self.last_updated_month = current_month

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'درباره ما'
        verbose_name_plural = 'درباره ما'
    def __str__(self):
        return self.email