from django.shortcuts import render, get_object_or_404
from django.db.models import Q
import difflib
from .models import Category, Product

def category_view(request, category_id):
    c = get_object_or_404(Category, id=category_id)
 
    return render(request, 'store/category.html', {
        'category': c, 
        'products': Product.objects.filter(categories=c), 
        'categories': Category.objects.all()
    })


def home(request): return render(request, 'store/home.html', {'categories': Category.objects.all(), 'products': Product.objects.filter(is_available=True)})
def product_detail(request, product_id): return render(request, 'store/product_detail.html', {'product': get_object_or_404(Product, id=product_id), 'categories': Category.objects.all()})
def search(request): return render(request, 'store/search_results.html') 
def about(request): return render(request, 'store/about.html')