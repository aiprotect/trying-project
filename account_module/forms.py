from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from . import models

User = get_user_model()


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور خود را وارد کنید'}),
        validators=[MinLengthValidator(8)]
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'})
    )
    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(attrs={'placeholder': 'ایمیل خود را وارد کنید'}),
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'نام خانوادگی'}),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تنظیم پیام‌های خطا برای هر فیلد
        self.fields['username'].error_messages = {
            'required': 'لطفا نام کاربری خود را وارد نمایید',
            'unique': 'این نام کاربری قبلا ثبت شده است',
            'invalid': 'نام کاربری فقط می‌تواند شامل حروف، اعداد و @/./+/-/_ باشد'
        }

        self.fields['email'].error_messages = {
            'required': 'لطفا ایمیل خود را وارد نمایید',
            'invalid': 'لطفا یک ایمیل معتبر وارد کنید',
            'unique': 'این ایمیل قبلا ثبت شده است'
        }

        self.fields['password1'].error_messages = {
            'required': 'لطفا کلمه عبور را تعیین کنید',
            'password_too_short': 'رمز عبور باید حداقل ۸ کاراکتر باشد',
            'password_too_common': 'این رمز عبور بسیار رایج است'
        }

        self.fields['password2'].error_messages = {
            'required': 'لطفا تکرار کلمه عبور را وارد کنید',
            'password_mismatch': 'کلمه‌های عبور با هم مطابقت ندارند'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلا ثبت شده است")
        return email
    




class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'نام کاربری',
            'dir': 'rtl'  # اضافه کردن جهت راست به چپ برای فیلدها
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'رمز عبور',
            'dir': 'rtl'  # اضافه کردن جهت راست به چپ برای فیلدها
        })




class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
    label="ایمیل",
    widget=forms.EmailInput(attrs={
        'placeholder': 'ایمیل خود را وارد کنید',
    }),
    required=True
)


class ModeLoginForgotPasswordForm(forms.Form):
    email = forms.EmailField(
    widget=forms.EmailInput(attrs={
        'readonly' : 'readonly',
        'class': 'readonly-input form-control email-input',
    }),
    required=True
)


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور جدید را وارد کنید',
            'autocomplete': 'new-password'  # اصلاح تایپو: autocplete -> autocomplete
        }),
        min_length=8,
        strip=True
    )

    confirm_password = forms.CharField(
        label='تایید رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور را مجددا وارد کنید',
            'autocomplete': 'new-password'  # اصلاح تایپو: autocplete -> autocomplete
        }),
        min_length=8,
        strip=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')  # اصلاح: conform -> confirm

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError('رمزهای عبور وارد شده یکسان نیستند')
        return cleaned_data
    

class ContactUsSupendedForm(forms.ModelForm):
    class Meta:
        model = models.ContactUsSupendedModel
        fields = ['subject', 'full_name', 'message', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control centered-placeholder', 
                'placeholder': 'ایمیل'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control centered-placeholder', 
                'placeholder': 'نام و نام خانوادگی'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control centered-placeholder', 
                'placeholder': 'عنوان'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control centered-placeholder', 
                'id': 'message', 
                'placeholder': 'متن پیام', 
                'rows': '5'
            }),
        }
       
        error_messages = {
            'email': {
                'required': 'لطفا ایمیل خود را وارد کنید.',
                'invalid': 'لطفا یک ایمیل معتبر وارد کنید.',
                'max_length': 'ایمیل نمی‌تواند بیشتر از 254 کاراکتر باشد.'
            },
            'full_name': {
                'required': 'نام و نام خانوادگی خود را وارد کنید',
                'max_length': 'نام نمی‌تواند بیشتر از 100 کاراکتر باشد.'
            },
            'subject': {
                'required': 'لطفا عنوان را وارد کنید.',
                'max_length': 'عنوان نمی‌تواند بیشتر از 200 کاراکتر باشد.'
            },
            'message': {
                'required': 'لطفا متن پیام را وارد کنید.',
                'max_length': 'پیام نمی‌تواند بیشتر از 1000 کاراکتر باشد.'
            }
        }


