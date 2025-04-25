from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404
from .models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from about_module.models import AboutUsModel
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from . import forms
from auth_manager.email_serice import AuthEmailService
from auth_manager.configs import AuthConfig
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as AuthLoginView
from django.http import HttpResponseForbidden
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import login
from django.http import Http404, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
User = get_user_model()


import random
from django.core.cache import cache
from django.shortcuts import render, redirect
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model

User = get_user_model()  # این همیشه مدل کاربر فعال را برمی‌گرداند

# Create your views here.

class RegisterView(View):
    success_url = reverse_lazy('index-page')
    template_name = 'account_module/register_page.html'
    form_class = forms.RegisterForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('index-page'))
        context = {'form': self.form_class(), 'title': 'ثبت نام کاربر جدید'}
        return render(request, self.template_name, context)
    
    def post(self, request):
        user_form = self.form_class(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.email_active_code = get_random_string(102)
            user.save()
            
            # ارسال ایمیل فعال‌سازی
            AuthEmailService.send_activation_email(user, request)
            
            # نمایش صفحه تأیید ارسال ایمیل
            return render(request, 'account_module/activation_sent.html', {
                'email': user.email,
                'title': 'ایمیل فعال‌سازی ارسال شد'
            })
        
        # اگر فرم معتبر نبود
        return render(request, self.template_name, {
            'title': 'ثبت نام کاربر جدید',
            'form': user_form
        })



@login_required
def account_inactive_error(request):
    about_us = AboutUsModel.objects.all().first()
    context = {
        'about' : about_us
    }
    return render(request, 'account_module/suspended.html',context)

class ResendActivationView(View):
    def get(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            # ارسال مجدد ایمیل فعال‌سازی
            AuthEmailService.send_activation_email(request.user, request)
            messages.info(request, 'ایمیل فعال‌سازی مجدداً ارسال شد.')
        return redirect('login-page')
    
class ActiveAccountView(View):
    def get(self, request, email_active_code):
        try:
            user = User.objects.get(email_active_code__iexact=email_active_code)
            if not user.is_active:
                user.is_active = True
                user.email_active_code = get_random_string(102)  # کد جدید برای امنیت
                user.save()
                # login(request, user)  # کاربر را به طور خودکار وارد سیستم می‌کند
                messages.success(request, 'حساب کاربری شما با موفقیت فعال شد!')
                return redirect(reverse('login-page'))
            else:
                messages.info(request, 'حساب کاربری شما قبلاً فعال شده است.')
                return redirect(reverse('index-page'))
        except User.DoesNotExist:
            messages.error(request, 'لینک فعال‌سازی نامعتبر است یا منقضی شده.')
            return redirect(reverse('register-page'))





class LoginView(AuthLoginView):
    template_name = 'account_module/login_page.html'
    form_class = forms.LoginForm
    success_url = reverse_lazy('index-page')

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_active:
            messages.error(self.request, 'حساب کاربری شما فعال نشده است. لطفاً ایمیل خود را بررسی کنید.')
            return self.form_invalid(form)

        login(self.request, user)
        messages.success(self.request, 'ورود شما با موفقیت انجام شد!')

        # ارسال ایمیل خوشامدگویی
        AuthEmailService.message_welcome_login(user, self.request)

        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.success_url

# Logout Account Logic
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request, 'شما با موفقیت خارج شدید')
        return redirect(reverse('index-page'))

def custom_404_view(request, exception):
    return render(request, 'account_module/404.html', status=404)
        

# Forgot Password Logic
class ForgetPasswordView(View):
    form = forms.ForgotPasswordForm
    def get(self, request):
        form = forms.ForgotPasswordForm
        context = {'email' : form}
        return render(request, 'account_module/forget_password.html', context)

    def post(self, request):
        forgot_password_form = self.form(request.POST)
        if forgot_password_form.is_valid():
            user_email = forgot_password_form.cleaned_data.get('email')
            user = User.objects.filter(email__iexact=user_email).first()
            if user is not None:
                AuthEmailService.send_password_reset_email(user, request)
                return redirect('login-page')  # هدایت به صفحه ورود


class ResetPasswordView(View):
    def get(self, request, *args, **kwargs):
        # دریافت کد فعال‌سازی از پارامتر URL
        active_code = kwargs.get('active_code')
        user = User.objects.filter(email_active_code=active_code).first()

        if not user:
            messages.error(request, "لینک بازیابی نامعتبر یا منقضی شده است")
            return redirect(reverse('login-page'))

        form = forms.ResetPasswordForm()
        return render(request, 'account_module/reset_password.html', {
            'form': form,
            'active_code': active_code  # ارسال کد به تمپلیت
        })

    def post(self, request, *args, **kwargs):
        active_code = kwargs.get('active_code')
        user = User.objects.filter(email_active_code=active_code).first()

        if not user:
            messages.error(request, "لینک بازیابی نامعتبر یا منقضی شده است")
            return redirect(reverse('login-page'))

        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.email_active_code = get_random_string(72)  # غیرفعال کردن کد قبلی
            user.save()

            messages.success(request, "رمز عبور شما با موفقیت تغییر یافت")
            return redirect(reverse('login-page'))

        return render(request, 'account_module/reset_password.html', {
            'form': form,
            'active_code': active_code
        })





class SuperUserChangePasswordView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        form = forms.ResetPasswordForm()
        return render(request, 'account_module/superuser_reset_password.html', {'form': form})

    def post(self, request):
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            logout(request)
            messages.success(request, "رمز عبور با موفقیت تغییر یافت. لطفاً مجدداً وارد شوید.")
            return redirect('login-page')

        return render(request, 'account_module/superuser_reset_password.html', {'form': form})


#   Password change logic during login
class ModeLoginForgotPasswordView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # برای کاربران لاگین کرده
            form = forms.ModeLoginForgotPasswordForm(initial={'email': request.user.email})
            return render(request, 'account_module/forget_password_auth.html', {
                'form': form,
                'user_authenticated': True
            })

    def post(self, request):
        form = forms.PasswordResetForm(request.POST)
        if form.is_valid():
            AuthEmailService.send_password_reset_email(request.user, request)
            logout(request)
            return redirect('login-page')  # هدایت به صفحه ورود

        return render(request, 'account_module/forget_password_auth.html', {
            'form': form,
            'message': 'خطا در ارسال ایمیل',
            'success': False
        })



class SupendedContactView(View):
    def get(self, request: HttpRequest):
        if not request.user.is_authenticated:
            return redirect(reverse('login-page') + f'?next={request.path}')
            
        if request.user.account_suspension:
            form = forms.ContactUsSupendedForm()
            contact_info = AboutUsModel.objects.filter(is_active=True).first()
            context = {
                'form' : form,
                'form_info' : contact_info
            }
            return render(request, 'account_module/contact_supended_user.html', context)
        return redirect(reverse('index-page'))

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login-page') + f'?next={request.path}')
            
        form = forms.ContactUsSupendedForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد.')
            return redirect(reverse('suspended-page'))
        
        messages.error(request, 'لطفا خطاهای فرم را اصلاح کنید.')
        return render(request, 'account_module/contact_supended_user.html', {'form': form})