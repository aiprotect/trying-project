from django.shortcuts import render, redirect
from django.urls import reverse
from . import models
from . import forms
from django.views import View
from django.views.generic.edit import FormView,CreateView
from django.urls import reverse
from about_module.models import *
import time
from django.contrib import messages
from django.http import JsonResponse
# class ContactUsView(CreateView):
#     template_name = 'contact_module/contact_page.html'
#     form_class = forms.ContactUsModelForm
#     # model = models.ContactUs 
#     success_url = 'http://localhost:8000/'


# class ContactUsView(FormView):
#     template_name = 'contact_module/contact_page.html'
#     form_class = forms.ContactUsModelForm
#     success_url = 'http://localhost:8000/'
    
#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)




def store_file(file):
    with open('temp/image.jpg', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)



class ContactUsView(View):
    def get(self, request):
        contact_form = forms.ContactUsModelForm()
        about_us = AboutUsModel.objects.filter(is_active_view=True).first()
       
        return render(request, 'contact_module/contact_page.html', {'contact_form': contact_form,'about_us' : about_us})

    def post(self, request):
        contact_form = forms.ContactUsModelForm(request.POST, request.FILES)
        if contact_form.is_valid():
            
            
            contact_form.save()

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('index-page')
            })

        return JsonResponse({
            'success': False,
            'errors': contact_form.errors
        }, status=400)
