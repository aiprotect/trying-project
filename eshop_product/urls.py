from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from account_module.views import custom_404_view  # اگر از ویوی سفارشی استفاده می‌کنید

handler404 = custom_404_view  # یا 'your_app.views.custom_404_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account_module.urls')),  
    path('products/', include('product_module.urls')),
    path('', include('home_module.urls')),
    path('', include('contact_module.urls')),
    path('', include('about_module.urls')),
    path('', include('panel_module.urls')),
    path('chat/', include('chat_module.urls')),

]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)