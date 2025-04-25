from django.conf import settings
from django.utils.html import format_html
from django.core.exceptions import ValidationError
import random as rnd
import jalali_date
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import slugify
from django_jalali.db import models as jmodels
from django.utils import timezone
from faker.generator import random
from jalali_date import date2jalali, datetime2jalali
from spacy import blank
import uuid
import string
from django.core.files.images import get_image_dimensions
from django.db.models.signals import pre_save
from django.dispatch import receiver


def generate_short_id(length=8):
    """
    تابع برای تولید شناسه کوتاه تصادفی
    Args:
        length (int): طول شناسه مورد نظر (پیش‌فرض 8 کاراکتر)
    Returns:
        str: رشته تصادفی متشکل از حروف و اعداد
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class ProductCategory(models.Model):
    """
    مدل دسته‌بندی محصولات
    این مدل برای سازماندهی محصولات در دسته‌بندی‌های مختلف استفاده می‌شود
    """
    title = models.CharField(max_length=200, verbose_name='عنوان دسته بندی')
    url = models.SlugField(
        verbose_name='آدرس URL',
        blank=True,
        help_text='این بخش به صورت خودکار از عنوان دسته‌بندی ایجاد می‌شود'
    )
    # class_name = models.CharField(
    #     max_length=100,
    #     verbose_name = 'ایکون دسته بندی '
    # )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='دسته‌بندی والد'
    )
    is_active = models.BooleanField(verbose_name='فعال/غیرفعال', default=True)
    is_delete = models.BooleanField(verbose_name='حذف شده/نشده', default=False)

    # constants.py
    CATEGORY_ICON_CHOICES = [
    # لوازم الکترونیکی
    ('fas fa-mobile-alt', 'موبایل'),
    ('fas fa-laptop', 'لپ‌تاپ'),
    ('fas fa-tablet-alt', 'تبلت'),
    ('fas fa-headphones', 'هدفون'),
    ('fas fa-keyboard', 'کیبورد'),
    ('fas fa-mouse', 'ماوس'),
    ('fas fa-desktop', 'کامپیوتر'),
    ('fas fa-print', 'پرینتر'),
    ('fas fa-server', 'سرور'),
    ('fas fa-hdd', 'هارد دیسک'),
    ('fas fa-memory', 'رم'),
    ('fas fa-microchip', 'پردازنده'),
    
    # لوازم خانگی
    ('fas fa-tv', 'تلویزیون'),
    ('fas fa-refrigerator', 'یخچال'),
    ('fas fa-blender', 'مخلوط کن'),
    ('fas fa-fan', 'پنکه'),
    ('fas fa-oven', 'اجاق گاز'),
    ('fas fa-utensils', 'وسایل آشپزخانه'),
    
    # پوشاک
    ('fas fa-tshirt', 'لباس مردانه'),
    ('fas fa-female', 'لباس زنانه'),
    ('fas fa-child', 'لباس کودک'),
    ('fas fa-socks', 'جوراب'),
    ('fas fa-shoe-prints', 'کفش'),
    ('fas fa-mitten', 'دستکش'),
    
    # کتاب و لوازم تحریر
    ('fas fa-book', 'کتاب'),
    ('fas fa-book-open', 'مجله'),
    ('fas fa-pencil-alt', 'مداد'),
    ('fas fa-pen', 'خودکار'),
    ('fas fa-ruler', 'خط کش'),
    ('fas fa-calculator', 'ماشین حساب'),
    
    # ورزشی
    ('fas fa-dumbbell', 'ورزشی'),
    ('fas fa-basketball-ball', 'توپ بسکتبال'),
    ('fas fa-futbol', 'توپ فوتبال'),
    ('fas fa-bicycle', 'دوچرخه'),
    ('fas fa-swimming-pool', 'استخر'),
    
    # زیبایی و سلامت
    ('fas fa-spa', 'زیبایی'),
    ('fas fa-pump-soap', 'شوینده'),
    ('fas fa-pills', 'دارو'),
    ('fas fa-first-aid-kit', 'کیت کمک‌های اولیه'),
    
    # سایر
    ('fas fa-gamepad', 'بازی و سرگرمی'),
    ('fas fa-camera', 'دوربین'),
    ('fas fa-car', 'خودرو'),
    ('fas fa-baby-carriage', 'کودک'),
    ('fas fa-tools', 'ابزار'),
    ('fas fa-plug', 'لوازم برقی'),
]

    icon = models.CharField(
        max_length=50,
        choices=CATEGORY_ICON_CHOICES,
        null=True,
        blank=True,
        verbose_name='آیکون',
        help_text='آیکون مناسب برای این دسته‌بندی را انتخاب کنید'
    )
    image = models.ImageField(
        upload_to='product_category/',
        null=True,
        blank=True,
        verbose_name='تصویر دسته‌بندی'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='توضیحات دسته‌بندی'
    )
    meta_title = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        verbose_name='عنوان متا (SEO)'
    )
    meta_description = models.CharField(
        max_length=160,
        null=True,
        blank=True,
        verbose_name='توضیحات متا (SEO)'
    )
    created_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = jmodels.jDateTimeField(
        auto_now=True,
        verbose_name='تاریخ آخرین ویرایش'
    )

    def save(self, *args, **kwargs):
        """ذخیره خودکار slug از عنوان دسته‌بندی"""
        if not self.url:
            self.url = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """آدرس URL برای دسترسی به صفحه دسته‌بندی"""
        return reverse('products_by_category', args=[self.url])

    class Meta:
        verbose_name = 'دسته‌بندی محصول'
        verbose_name_plural = 'دسته‌بندی محصولات'
        ordering = ['title']
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['is_active']),
        ]


class ProductBrand(models.Model):
    """
    مدل برند محصولات
    این مدل برای مدیریت برندهای مختلف محصولات استفاده می‌شود
    """
    title = models.CharField(max_length=30, verbose_name='نام برند')
    logo = models.ImageField(
        upload_to='product_brands/',
        null=True,
        blank=True,
        verbose_name='لوگو برند'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='توضیحات برند'
    )
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name='وبسایت برند'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیرفعال'
    )
    meta_title = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        verbose_name='عنوان متا (SEO)'
    )
    meta_description = models.CharField(
        max_length=160,
        null=True,
        blank=True,
        verbose_name='توضیحات متا (SEO)'
    )
    created_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = jmodels.jDateTimeField(
        auto_now=True,
        verbose_name='تاریخ آخرین ویرایش'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """آدرس URL برای دسترسی به صفحه برند"""
        return reverse('products_by_brand', args=[slugify(self.title)])

    class Meta:
        verbose_name = 'برند محصول'
        verbose_name_plural = 'برندهای محصولات'
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['is_active']),
        ]


class ProductSpecification(models.Model):
    """
    مدل مشخصات فنی محصول
    این مدل برای تعریف ویژگی‌های فنی مشترک بین محصولات استفاده می‌شود
    """
    name = models.CharField(
        max_length=100,
        verbose_name='نام مشخصه'
    )
    category = models.ForeignKey(
        ProductCategory,
        related_name='specifications',
        on_delete=models.CASCADE,
        verbose_name='دسته‌بندی مربوطه'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'مشخصه فنی'
        verbose_name_plural = 'مشخصات فنی'
        ordering = ['name']


class ProductColor(models.Model):
    """
    مدل رنگ‌های محصول
    این مدل برای مدیریت رنگ‌های مختلف محصولات استفاده می‌شود
    """
    name = models.CharField(
        max_length=50,
        verbose_name='نام رنگ'
    )
    hex_code = models.CharField(
        max_length=7,
        verbose_name='کد HEX رنگ',
        help_text='مثلاً #FFFFFF برای سفید'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیرفعال'
    )

    def __str__(self):
        return self.name

    def color_preview(self):
        """پیش‌نمایش رنگ در پنل مدیریت"""
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; background-color: {};"></span>',
            self.hex_code
        )
    color_preview.short_description = 'پیش‌نمایش'

    class Meta:
        verbose_name = 'رنگ محصول'
        verbose_name_plural = 'رنگ‌های محصولات'
        ordering = ['name']


class ProductSize(models.Model):
    """
    مدل سایزهای محصول
    این مدل برای مدیریت سایزهای مختلف محصولات استفاده می‌شود
    """
    title = models.CharField(
        max_length=20,
        verbose_name='عنوان سایز'
    )
    description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='توضیحات سایز'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیرفعال'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'سایز محصول'
        verbose_name_plural = 'سایزهای محصولات'
        ordering = ['title']


class Product(models.Model):
    """
    مدل اصلی محصولات
    این مدل تمامی اطلاعات مربوط به محصولات فروشگاه را نگهداری می‌کند
    """
    # اطلاعات اصلی محصول
    title = models.CharField(
        max_length=300,
        verbose_name='عنوان محصول'
    )
    english_title = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name='عنوان انگلیسی محصول',
        help_text='برای استفاده در SEO و URLها'
    )
    sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='کد SKU محصول',
        help_text='کد انبارداری محصول (Stock Keeping Unit)'
    )
    price = models.PositiveIntegerField(
        verbose_name='قیمت اصلی',
        validators=[MinValueValidator(10000)],
        help_text='قیمت به ریال'
    )
    discount_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='قیمت با تخفیف'
    )
    
    short_description = models.CharField(
        max_length=360,
        null=True,
        blank=True,
        verbose_name='توضیحات کوتاه'
    )
    description = models.TextField(
        verbose_name='توضیحات کامل محصول',
        null=True,
        blank=True
    )

    # وضعیت محصول
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیرفعال'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='محصول ویژه'
    )
    is_bestseller = models.BooleanField(
        default=False,
        verbose_name='پرفروش'
    )
    is_new = models.BooleanField(
        default=False,
        verbose_name='محصول جدید'
    )
    is_delete = models.BooleanField(
        default=False,
        verbose_name='حذف شده/نشده'
    )

    # موجودی و انبارداری
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد موجودی'
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        verbose_name='حداقل موجودی هشدار'
    )
    manage_stock = models.BooleanField(
        default=True,
        verbose_name='مدیریت موجودی'
    )
    backorder_allowed = models.BooleanField(
        default=False,
        verbose_name='مجاز به پیش‌خرید'
    )
    sold_individually = models.BooleanField(
        default=False,
        verbose_name='فروش تکی اجباری'
    )
    # favorite product

    favorited_by = models.ManyToManyField(
        'account_module.User',
        verbose_name='کاربرانی که این محصول را پسندیدند',
        # تغییر related_name به یک نام منحصر به فرد
        related_name='products_they_favorited'
    )

    # اطلاعات فنی
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='وزن (گرم)',
        help_text='وزن محصول به گرم'
    )
    internal_memory = models.IntegerField(
        null=True,
        blank=False,
        verbose_name='حافظه داخلی'
    )
    selfie_camera = models.IntegerField(
        null=True,
        blank=False,
        verbose_name='دوربین سلفی ',
        help_text='مگاپیکسل'
    )
    operating_system = models.CharField(
        max_length=48,
        null=True,
        blank=False,
        verbose_name='سیستم عامل ',
    )
    finally_version = models.BooleanField(
        default=True,
        verbose_name='نسخه سیستم نهایی'
    )
    is_update_system = models.BooleanField(
        default=True,
        null=False,
        blank=False,
        verbose_name='قابل ارتقاع به نسخه های بالاتر',
        help_text='قابلیت اپدیت سیستم عامل'
    )
    dimensions = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='ابعاد محصول',
        help_text='به صورت طول × عرض × ارتفاع'
    )
    material = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='جنس محصول'
    )
    memory_ram = models.IntegerField(
        null=True,
        blank=False,
        verbose_name='حافظه RAM'
    )
    battery_life = models.IntegerField(
        null=True,
        blank=False,
        verbose_name='میلی امپر ساعت'
    )
    SIM_SELECTED = [
        (' تک سیمکارت', 'SIM1'),
        ('دو سیمکارت', 'SIM2'),
        ('سه سیمکارت', 'SIM3')
    ]
    sim_number = models.CharField(
        choices=SIM_SELECTED,
        max_length=20,
        verbose_name='ظرفیت سیمکارت ',
        null=True,
        blank=False
    )

    # روابط
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='دسته‌بندی محصول',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    brand = models.ForeignKey(
        ProductBrand,
        verbose_name='برند محصول',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    related_products = models.ManyToManyField(
        'self',
        blank=True,
        verbose_name='محصولات مرتبط'
    )

    # تصاویر
    main_image = models.ImageField(
        upload_to='products/main/',
        verbose_name='تصویر اصلی محصول'
    )
    thumbnail = models.ImageField(
        upload_to='products/thumbnails/',
        null=True,
        blank=True,
        verbose_name='تصویر بندانگشتی'
    )

    # SEO و URL
    url = models.SlugField(
        max_length=300,
        unique=True,
        verbose_name='آدرس URL',
        help_text='آدرس SEO-friendly برای محصول'
    )
    meta_title = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        verbose_name='عنوان متا (SEO)'
    )
    meta_description = models.CharField(
        max_length=160,
        null=True,
        blank=True,
        verbose_name='توضیحات متا (SEO)'
    )
    meta_keywords = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='کلمات کلیدی متا (SEO)'
    )

    # تاریخ‌ها
    created_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = jmodels.jDateTimeField(
        auto_now=True,
        verbose_name='تاریخ آخرین ویرایش'
    )
    publish_date = jmodels.jDateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ انتشار'
    )



    class ProductStatus(models.TextChoices):
        DRAFT = 'draft', 'پیش‌نویس'
        PENDING = 'pending', 'در انتظار بررسی'
        PUBLISHED = 'published', 'منتشر شده'
        ARCHIVED = 'archived', 'بایگانی شده'

    status = models.CharField(
        max_length=10,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
        verbose_name='وضعیت محصول'
    )

    def get_price_difference(self):
        return self.price - self.discount_price

   

    @property
    def active_discount(self):
        """تخفیف فعال فعلی برای محصول را برمی‌گرداند"""
        now = timezone.now()
        return self.discounts.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()
    
    @property
    def final_price(self):
       return self.discount_price if self.discount_price is not None else self.price

    @property
    def has_discount(self):
      return self.discount_price is not None

    @property
    def discount_percentage(self):
      if self.has_discount:
        return int(((self.price - self.discount_price) / self.price) * 100)
      return 0

    def clean(self):
        if self.finally_version and self.is_update_system:
            raise ValidationError(
                "محصول نمی‌تواند همزمان هم نسخه نهایی باشد هم قابل ارتقا. فقط یکی از گزینه‌ها باید انتخاب شود."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        """ذخیره خودکار slug و SKU"""
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"

        if not self.url:
            base_slug = slugify(
                self.english_title) if self.english_title else slugify(self.title)
            self.url = f"{base_slug}-{uuid.uuid4().hex[:4]}"

        # ایجاد خودکار thumbnail اگر وجود نداشته باشد
        if self.main_image and not self.thumbnail:
            # در اینجا می‌توانید از کتابخانه‌هایی مانند Pillow برای ایجاد thumbnail استفاده کنید
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """آدرس URL برای دسترسی به صفحه محصول"""
        return reverse('product-detail', args=[self.url])

    def get_price(self):
        """دریافت قیمت نهایی (با احتساب تخفیف)"""
        return self.discount_price if self.discount_price else self.price

    def is_in_stock(self):
        """بررسی موجود بودن محصول"""
        return self.stock_quantity > 0

    def is_on_sale(self):
        """بررسی وجود تخفیف"""
        return self.discount_price is not None and self.discount_price < self.price

    def get_discount_percentage(self):
        """درصد تخفیف محصول"""
        if self.is_on_sale():
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    def jalali_created_at(self):
        """تاریخ ایجاد به شمسی"""
        return datetime2jalali(self.created_at)
    jalali_created_at.short_description = 'تاریخ ایجاد'

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['sku']),
            models.Index(fields=['price']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_bestseller']),
            models.Index(fields=['status']),
        ]


class ProductVariant(models.Model):
    # ...
    
    @property
    def final_price(self):
        """قیمت نهایی واریانت (با احتساب تخفیف محصول اصلی یا تخفیف خاص واریانت)"""
        if self.discount_price is not None:
            return self.discount_price
        elif self.product.has_discount:
            return self.product.discount_price
        return self.price if self.price is not None else self.product.price

# Products Discount Price 
class Discount(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='discounts',
        verbose_name='محصول'
    )
    percentage = models.PositiveIntegerField(
        verbose_name='درصد تخفیف',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='درصد تخفیف (1 تا 100)'
    )
    start_date = models.DateTimeField(verbose_name='تاریخ شروع')
    end_date = models.DateTimeField(verbose_name='تاریخ پایان')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # محاسبه قیمت با تخفیف و ذخیره آن
        self.product.discount_price = self.discounted_price
        self.product.save()
    
    class Meta:
        verbose_name = 'تخفیف'
        verbose_name_plural = 'تخفیف‌ها'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.percentage}% تخفیف برای {self.product.title}"

    @property
    def discounted_price(self):
        return self.product.price * (100 - self.percentage) // 100

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

@receiver([post_save, post_delete], sender=Discount)
def update_product_discount(sender, instance, **kwargs):
    product = instance.product
    active_discount = product.active_discount  # از propertyای که قبلا تعریف کردید استفاده می‌کنیم
    
    if active_discount:
        product.discount_price = active_discount.discounted_price
    else:
        product.discount_price = None
    
    product.save()

class ProductImage(models.Model):
    """
    مدل تصاویر محصول
    این مدل برای مدیریت چندین تصویر برای هر محصول استفاده می‌شود
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='محصول'
    )
    image = models.ImageField(
        upload_to='products/images/',
        verbose_name='تصویر'
    )
    alt_text = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='متن جایگزین (alt)',
        help_text='برای دسترسی‌پذیری و SEO'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='تصویر اصلی'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب نمایش'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    def __str__(self):
        return f"تصویر {self.id} برای محصول {self.product.title}"

    def save(self, *args, **kwargs):
        """اگر این تصویر به عنوان اصلی علامت خورده، سایر تصاویر را غیر اصلی می‌کند"""
        if self.is_main:
            ProductImage.objects.filter(product=self.product).exclude(
                id=self.id).update(is_main=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصولات'
        ordering = ['order']
        unique_together = ('product', 'is_main')


class ProductVariant(models.Model):
    """
    مدل انواع محصول (Variant)
    این مدل برای مدیریت انواع مختلف یک محصول (مانند رنگ‌ها و سایزهای مختلف) استفاده می‌شود
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name='محصول پایه'
    )
    color = models.ForeignKey(
        ProductColor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='رنگ'
    )
    size = models.ForeignKey(
        ProductSize,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='سایز'
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد SKU نوع محصول'
    )
    price = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='قیمت (در صورت متفاوت بودن)'
    )
    discount_price = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='قیمت با تخفیف'
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد موجودی'
    )
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='تصویر مرتبط'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیرفعال'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    def __str__(self):
        variant_name = []
        if self.color:
            variant_name.append(str(self.color))
        if self.size:
            variant_name.append(str(self.size))
        return f"{self.product.title} - {' - '.join(variant_name)}" if variant_name else self.product.title

    def save(self, *args, **kwargs):
        """تولید خودکار SKU"""
        if not self.sku:
            base_sku = self.product.sku
            variant_part = []
            if self.color:
                variant_part.append(self.color.name[:3].upper())
            if self.size:
                variant_part.append(self.size.title[:3].upper())
            self.sku = f"{base_sku}-{'-'.join(variant_part)}" if variant_part else f"{base_sku}-VAR"
        super().save(*args, **kwargs)

    def get_price(self):
        """دریافت قیمت نهایی (با احتساب تخفیف)"""
        if self.price is not None:
            return self.discount_price if self.discount_price else self.price
        return self.product.get_price()

    class Meta:
        verbose_name = 'نوع محصول'
        verbose_name_plural = 'انواع محصولات'
        unique_together = ('product', 'color', 'size')
        ordering = ['product', 'color', 'size']


class ProductSpecificationValue(models.Model):
    """
    مدل مقادیر مشخصات فنی محصول
    این مدل برای ذخیره مقادیر واقعی مشخصات فنی هر محصول استفاده می‌شود
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name='محصول'
    )
    specification = models.ForeignKey(
        ProductSpecification,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='مشخصه فنی'
    )
    value = models.CharField(
        max_length=200,
        verbose_name='مقدار'
    )

    def __str__(self):
        return f"{self.specification.name}: {self.value} برای {self.product.title}"

    class Meta:
        verbose_name = 'مقدار مشخصه فنی'
        verbose_name_plural = 'مقادیر مشخصات فنی'
        unique_together = ('product', 'specification')


class ProductTag(models.Model):
    """
    مدل تگ‌های محصول
    این مدل برای افزودن تگ‌های مختلف به محصولات استفاده می‌شود
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='نام تگ'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug تگ'
    )
    products = models.ManyToManyField(
        Product,
        related_name='tags',
        blank=True,
        verbose_name='محصولات'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ذخیره خودکار slug"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """آدرس URL برای دسترسی به صفحه تگ"""
        return reverse('products_by_tag', args=[self.slug])

    class Meta:
        verbose_name = 'تگ محصول'
        verbose_name_plural = 'تگ‌های محصولات'
        ordering = ['name']


class ProductReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='کاربر'
    )
    product = models.ForeignKey(
        'Product',  # تغییر این خط
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='محصول'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='نام نظر دهنده'
    )
    email = models.EmailField(
        verbose_name='ایمیل نظر دهنده'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز (1-5)'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان نظر'
    )
    comment = models.TextField(
        verbose_name='متن نظر'
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='تایید شده'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ ویرایش'
    )

    def __str__(self):
        return f"نظر {self.id} برای محصول {self.product.title}"

    def get_rating_stars(self):
        """نمایش امتیاز به صورت ستاره"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    get_rating_stars.short_description = 'امتیاز'

    class Meta:
        verbose_name = 'نظر محصول'
        verbose_name_plural = 'نظرات محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['rating']),
        ]


class ProductAttribute(models.Model):
    """
    مدل ویژگی‌های محصول
    این مدل برای تعریف ویژگی‌های دلخواه برای محصولات استفاده می‌شود
    """
    name = models.CharField(
        max_length=100,
        verbose_name='نام ویژگی'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Slug ویژگی'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='توضیحات'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصولات'
        ordering = ['name']


class ProductAttributeValue(models.Model):
    """
    مدل مقادیر ویژگی‌های محصول
    این مدل برای ذخیره مقادیر ویژگی‌های هر محصول استفاده می‌شود
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name='محصول'
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='ویژگی'
    )
    value = models.CharField(
        max_length=250,
        verbose_name='مقدار'
    )

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        verbose_name = 'مقدار ویژگی محصول'
        verbose_name_plural = 'مقادیر ویژگی‌های محصولات'
        unique_together = ('product', 'attribute')
