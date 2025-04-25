from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, ContactUsSupendedModel, AboutUsModel, UserActivity

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1
    fields = ('birth_date', 'national_code', 'gender', 'phone_number')
    readonly_fields = ('formatted_birth_date', 'age')

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'full_name', 'profile_image')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser','account_suspension', 'groups', 'user_permissions')}),
        ('تاریخ‌های مهم', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(ContactUsSupendedModel)
admin.site.register(AboutUsModel)
admin.site.register(UserActivity)