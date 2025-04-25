from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from .models import (
    Product, ProductCategory, ProductBrand,
    ProductTag, ProductImage, ProductVariant,
    ProductSpecification, ProductSpecificationValue,
    ProductColor, ProductSize, ProductReview,
    ProductAttribute, ProductAttributeValue,Discount
)

## ------------------- فیلترهای سفارشی -------------------
class ActiveStatusFilter(admin.SimpleListFilter):
    title = 'وضعیت فعال'
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'فعال'),
            ('inactive', 'غیرفعال')
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)


## ------------------- اینلاین‌ها -------------------
class ProductImagesInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'image_preview', 'alt_text', 'is_main', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit: cover;" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'پیش‌نمایش'


## ------------------- ادمین دسته‌بندی محصولات -------------------
@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['title', 'parent', 'product_count', 'is_active']
    list_filter = [ActiveStatusFilter, 'parent']
    search_fields = ['title', 'description']
    prepopulated_fields = {'url': ['title']}
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'url', 'parent', 'description')
        }),
        ('تصاویر و آیکون', {
            'fields': ('icon', 'image')
        }),
        ('تنظیمات SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('وضعیت', {
            'fields': ('is_active', 'is_delete')
        })
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'تعداد محصولات'


## ------------------- ادمین برند محصولات -------------------
@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ['title', 'website', 'is_active']
    list_filter = [ActiveStatusFilter]
    search_fields = ['title', 'description']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'logo', 'website', 'description')
        }),
        ('تنظیمات SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        })
    )


## ------------------- ادمین محصولات اصلی -------------------
@admin.register(Product)
class ProductAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['title', 'category', 'brand', 'price', 'stock_status', 'is_active']
    list_filter = [ActiveStatusFilter, 'category', 'brand']
    search_fields = ['title', 'sku', 'description']
    list_editable = ['is_active']
    prepopulated_fields = {'url': ['title']}
    inlines = [ProductImagesInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'english_title', 'url', 'sku', 'category', 'brand')
        }),
        ('قیمت و موجودی', {
            'fields': ('price', 'stock_quantity', 'low_stock_threshold','discount_price','backorder_allowed')
        }),
        ('تصاویر محصول', {
            'fields': ('main_image', 'thumbnail')
        }),
        ('توضیحات', {
            'fields': ('short_description', 'description')
        }),
        ('ویژگی‌های فنی', {
            'fields': ('weight', 'dimensions', 'material', 'selfie_camera', 'internal_memory','operating_system','is_update_system','finally_version','battery_life','memory_ram','sim_number')
        }),
        ('وضعیت محصول', {
            'fields': ('is_active', 'is_featured', 'is_bestseller', 'is_new', 'status')
        }),
        ('تنظیمات SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('محصولات مورد علاقه', {
        'fields': ('favorited_by',)  
    }),
       
    )
    
    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span style="color:red;">ناموجود</span>')
        elif obj.stock_quantity < obj.low_stock_threshold:
            return format_html('<span style="color:orange;">کم موجود ({})</span>', obj.stock_quantity)
        return format_html('<span style="color:green;">موجود ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'وضعیت موجودی'


## ------------------- ادمین رنگ‌های محصول -------------------
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active']
    list_filter = ['is_active']
    
    def color_display(self, obj):
        return format_html(
            '<div style="width:20px; height:20px; background-color:{}; display:inline-block;"></div> {}',
            obj.hex_code, obj.name
        )
    color_display.short_description = 'نمایش رنگ'


## ------------------- ادمین سایزهای محصول -------------------
@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'is_active']
    list_filter = ['is_active']


## ------------------- ادمین تگ‌های محصول -------------------
@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ['name']}


## ------------------- ادمین تخفیفات محصولات -------------------
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    # Your Discount admin configuration
    pass
    


## ------------------- ادمین نظرات محصول -------------------
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating_stars', 'is_approved']
    list_filter = ['is_approved', 'rating']
    list_editable = ['is_approved']
    
    def rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_stars.short_description = 'امتیاز'


## ------------------- ادمین انواع محصول -------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'size', 'price', 'stock_quantity']
    list_filter = ['color', 'size']


## ------------------- ادمین ویژگی‌های محصول -------------------
@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}


## ------------------- ادمین مقادیر ویژگی‌ها -------------------
@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['product', 'attribute', 'value']
    list_filter = ['attribute']