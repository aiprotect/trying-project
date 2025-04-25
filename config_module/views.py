from django.shortcuts import render
from django.views import View
from .models import *
from .models import SliderModel

# Create your views here.

def slider_context(request):
    slider = SliderModel.objects.filter(is_active=True).first()
    return {
        'slider': slider
    }