from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from .views import *

urlpatterns = [
    path('change-password/', user_passes_test(lambda u: u.is_superuser)(SuperUserChangePasswordView.as_view()),
         name='superuser-change-password'),
    path('register/', RegisterView.as_view(), name='register-page'),
    path('login/', LoginView.as_view(), name='login-page'),
    path('logout/', LogoutView.as_view(), name='logout-page'),
    path('activate/<email_active_code>/', ActiveAccountView.as_view(), name='activate-account'),
    path('resend-activation/', ResendActivationView.as_view(), name='resend-activation'),
    path('account/inactive/',account_inactive_error, name='suspended-page'),
    path('forget-pass/',ForgetPasswordView.as_view(), name='forget-pass-page'),
    path('reset-pass/<str:active_code>/', ResetPasswordView.as_view(), name='reset-pass-page'),
    path('mode-forgot-pass/', ModeLoginForgotPasswordView.as_view(), name='mode-forgot-pass'),
    path('contact-supended/', SupendedContactView.as_view(), name='contact-supended-page'),

]