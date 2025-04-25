from typing import Any
from django.db.models import Avg, Min, Max
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Product,ProductCategory,ProductBrand
from django.views.generic import ListView, DetailView
from django.views import View
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.generic import CreateView
from django.contrib import messages

from django.shortcuts import redirect
# Create your views here.

from django.views.generic import ListView
from django.core.paginator import Paginator
from .models import Product, ProductCategory
from django.db.models import Prefetch, Q, Count, Exists, OuterRef
from django.views.generic import ListView
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Product, ProductCategory, ProductBrand,Discount

def product_list(request):
    # دریافت پارامترهای جستجو و فیلتر
    category_slug = request.GET.get('category', None)
    sort = request.GET.get('sort', 'default')
    search_query = request.GET.get('q', None)
    
    # دریافت همه محصولات
    products = Product.objects.filter(is_active=True)
    
    # فیلتر بر اساس دسته‌بندی
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # جستجو در محصولات
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # مرتب‌سازی محصولات
    if sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'price-low':
        products = products.order_by('price')
    elif sort == 'price-high':
        products = products.order_by('-price')
    
    # صفحه‌بندی
    paginator = Paginator(products, 12)  # نمایش 12 محصول در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # دریافت دسته‌بندی‌ها برای نمایش در سایدبار
    categories = ProductCategory.objects.all()
    
    # # products discounts 
    # now = timezone.now()
    # active_discount = Discount.objects.filter(
    # is_active=True,
    # start_date__lte=now,
    # end_date__gte=now
    # ).exists()
    
    context = {
        'products': page_obj,
        # 'discount' : active_discount,
        'categories': categories,
        'current_category': category_slug,
        'sort': sort,
        'search_query': search_query,
    }
    
    return render(request, 'product_module/product_list.html', context)
    
@login_required
def toggle_favorite(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        if request.user in product.favorited_by.all():
            product.favorited_by.remove(request.user)
            is_favorited = False
        else:
            product.favorited_by.add(request.user)
            is_favorited = True
        
        return JsonResponse({
            'status': 'success',
            'is_favorited': is_favorited,
            'favorite_count': product.favorited_by.count()
        })
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_module/product_detail.html'
    context_object_name = 'product'
    slug_field = 'url'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        now = timezone.now()
        active_discount = product.discounts.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
        ).exists()
    
        context['discount'] = active_discount 
        
        # محاسبه میانگین امتیازها
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['avg_rating'] = round(avg_rating, 1)
        
        # تصاویر محصول
        context['images'] = product.images.all().order_by('order')

        # تخفیفات محصول
        context['discount'] = Discount.objects.filter(is_active=True).exists()
        
        # محصولات مرتبط
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        return context
    
class FeaturedProductsView(ListView):
    template_name = 'products/featured_products.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(
            is_featured=True,
            is_active=True
        ).select_related('category', 'brand')[:8]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_categories'] = ProductCategory.objects.filter(
            is_featured=True,
            is_active=True
        )[:3]
        return context
    

def compare_products(request):
    product_ids = request.GET.getlist('products')
    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True
    ).prefetch_related('specifications', 'images')
    
    # جمع‌آوری تمام مشخصات فنی برای نمایش مقایسه
    all_specs = {}
    for product in products:
        for spec in product.specifications.all():
            all_specs[spec.specification.name] = all_specs.get(spec.specification.name, []) + [spec.value]
    
    return render(request, 'products/compare.html', {
        'products': products,
        'specifications': all_specs
    })

class ProductSearchView(ListView):
    template_name = 'products/product_search.html'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query),
                is_active=True
            ).select_related('category', 'brand')
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
    