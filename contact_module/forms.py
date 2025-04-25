from django import forms
from django.core import validators
from . import models

# class ContactUsForm(forms.Form):
#     full_name = forms.CharField(
#         label='نام و نام خانوادگی',
#         max_length=50,
#         help_text='Hi',
#         error_messages={
#             'required': 'لطفا نام و نام خانوادگی خود را وارد کنید',
#             'max_length': 'نام و نام خانوادگی نمی تواند بیشتر از 50 کاراکتر باشد'
#         },
#         widget=forms.TextInput(attrs={
#             'class': 'form-control centered-placeholder',  # اضافه کردن کلاس CSS
#             'placeholder': 'نام و نام خانوادگی',
#             'id': 'full_name'
#         })
#     )

#     email = forms.EmailField(
#         label='ایمیل',
#         required=True,
#         error_messages={
#             'required': 'لطفا ایمیل خود را وارد کنید',
#             'invalid': 'لطفا یک ایمیل معتبر وارد کنید'
#         },
#         widget=forms.EmailInput(attrs={
#             'class': 'form-control centered-placeholder',  # اضافه کردن کلاس CSS
#             'placeholder': 'ایمیل'
#         })
#     )

#     subject = forms.CharField(
#         label='عنوان',
#         widget=forms.TextInput(attrs={
#             'class': 'form-control centered-placeholder',  # اضافه کردن کلاس CSS
#             'placeholder': 'عنوان'
#         }),
#         error_messages={
#             'required': 'لطفا عنوان برای پیام خود درج نمایید'
#         }
#     )

#     message = forms.CharField(
#         label='متن پیام',
#         widget=forms.Textarea(attrs={
#             'class': 'form-control centered-placeholder',  # اضافه کردن کلاس CSS
#             'placeholder': 'متن پیام',
#             'rows': '5',
#             'id': 'message'
#         }),
#         error_messages={
#             'required': 'لطفا متن پیغام را تکمیل نمایید'
#         }
#     )


class ContactUsModelForm(forms.ModelForm):
    class Meta:
        model = models.ContactUs
        fields = ['subject', 'full_name', 'message', 'email', 'image']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control centered-placeholder', 'placeholder': 'ایمیل'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control centered-placeholder', 'placeholder': 'نام و نام خانوادگی'}),
            'subject': forms.TextInput(attrs={'class': 'form-control centered-placeholder', 'placeholder': 'عنوان'}),
            'message': forms.Textarea(attrs={'class': 'form-control centered-placeholder', 'id': 'message', 'placeholder': 'متن پیام', 'rows': '5'}),
            'image': forms.ClearableFileInput(),
        }
        def __init__(self, *args, **kwargs):
            super(ContactUsModelForm, self).__init__(*args, **kwargs)
            self.fields['image'].required = False  # Make the image field optional

        error_messages = {
            'email': {
                'required': 'لطفا ایمیل خود را وارد کنید.',
                'invalid': 'لطفا یک ایمیل معتبر وارد کنید.'
            },
            'full_name': {
                'required': 'نام و نام خانوادگی خود را وارد کنید'
            },
            'subject': {
                'required': 'لطفا عنوان را وارد کنید.'
            },
            'message': {
                'required': 'لطفا متن پیام را وارد کنید.'
            }
        }  # بسته شدن دیکشنری error_messages


class CreateProfileForm(forms.Form):
    image_profile = forms.ImageField(
        widget=forms.ClearableFileInput(),
        error_messages={'invalid': 'لطفا تصویری معتبر وارد کنید.'}
    )
