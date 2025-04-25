from django import forms
from account_module.models import UserProfile
from django.utils.translation import gettext_lazy as _
from django_jalali import forms as jforms
from account_module.models import User


class UserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
    label='تاریخ تولد',
    widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date',
        'format': '%Y-%m-%d'  # فرمت ISO
    }),
    input_formats=['%Y-%m-%d']  # فرمت‌های قابل قبول
)
    
    national_code = forms.CharField(
        label='کد ملی',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        error_messages={
            'required': 'لطفا کد ملی را وارد کنید',
            'invalid': 'کد ملی وارد شده معتبر نیست'
        }
    )

    profile_image = forms.ImageField(
        label='تصویر پروفایل',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    phone_number = forms.CharField(
        label='شماره موبایل',
        required=True,
        error_messages={
            'required': 'لطفا  شماره موبایل خود را وارد کنید',
            'invalid': ' شماره موبایل وارد شده معتبر نیست'
        }
    )

    class Meta:
        model = UserProfile
        fields = ['gender', 'birth_date', 'national_code', 'phone_number', 'address', 'city', 'profile_image']
        
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'gender': {
                'required': 'لطفا جنسیت را انتخاب کنید'
            }
        }