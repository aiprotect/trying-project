from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# from django.contrib.auth.models import User
from account_module.models import User




def chat_view(request):
    return render(request, 'chat_module/room.html')