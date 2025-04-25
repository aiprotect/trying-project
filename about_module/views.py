from django.shortcuts import render
from django.views import View
from .models import *
# Create your views here.

def about_us_context(request):
    about = AboutUsModel.objects.filter(is_active_view=True).first()
    return {'about': about}

class AboutUsView(View):
    def get(self, request):
        about = AboutUsModel.objects.filter(is_active_view=True).first()  # فقط رکورد فعال
        context = {
            'about': about  # ارسال یک شیء به تمپلیت
        }
        return render(request, 'about_module/about_us.html', context)