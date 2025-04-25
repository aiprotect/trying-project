from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.


class UserPanel(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'panel_module/user_panel.html')
        else:
            return redirect(reverse('login-page'))


@method_decorator(login_required, name='dispatch')
class ProfileEditView(View):
    form_class = UserProfileForm
    
    def get(self, request):
        profile = request.user.profile
        form = self.form_class(instance=profile)
        return render(request, 'panel_module/edit_profile.html', {'form': form})

    def post(self, request):
        profile = request.user.profile
        form = self.form_class(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'تغییرات با موفقیت ذخیره شدند')
            return redirect('profile_edit_page')
        else:
            # نمایش خطاهای فرم اگر معتبر نباشد
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
        
        return render(request, 'panel_module/edit_profile.html', {'form': form})