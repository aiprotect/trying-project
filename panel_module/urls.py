from django.urls import path
from .views import *

urlpatterns = [
    path('user-panel/', UserPanel.as_view(), name='dashboard'),
    path('user-panel/edite-profile/', ProfileEditView.as_view(), name='profile_edit_page')
]