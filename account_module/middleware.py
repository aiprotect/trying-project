from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import render


class SuspendedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # لیست صفحاتی که باید از چک تعلیق معاف باشند
        exempt_urls = [
            reverse('contact-us-page'),
            reverse('logout-page'),
            # می‌توانید صفحات دیگر را اینجا اضافه کنید
        ]
        
        # اگر کاربر لاگین کرده و صفحه از معافیت‌ها نیست
        if request.user.is_authenticated and request.path not in exempt_urls:
            if request.user.account_suspension:
                # اگر کاربر تعلیق شده است، صفحه تعلیق را نشان بده
                if request.path == reverse('contact-supended-page'):
                    return self.get_response(request)
                return render(request, 'account_module/suspended.html', status=403)
            else:
                # اگر کاربر تعلیق نشده اما در صفحه تعلیق است، به صفحه اصلی ریدایرکت کن
                if request.path == reverse('suspended-page'):
                    return redirect(reverse('index-page'))
        
        return self.get_response(request)