from django.urls import path
from .views import *

urlpatterns = [
    path('about-us/',AboutUsView.as_view(), name='about-us-page')
]