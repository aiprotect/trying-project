from django.urls import path
from . import views
urlpatterns = [
    path('', views.product_list, name='product-list'),
        path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),  # For product detail with short URL
]