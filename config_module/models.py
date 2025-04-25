from django.db import models

# Create your models here.

class SliderModel(models.Model):
    title = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='عنوان اسلایدر'
    )
    short_description = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='توضیحات کوتاه اسلایدر'
    )
    image_slider = models.ImageField(
        upload_to='slider_images',
        null=False,
        blank=False,
        verbose_name='تصویر اسلایدر'
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name='فعال/غیرفعال'
    )

    class Meta:
        verbose_name = 'اسلایدر صفحه'
        verbose_name_plural = 'اسلایدر های صفحه'

    def __str__(self):
        return self.title

