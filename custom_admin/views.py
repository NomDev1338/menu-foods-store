from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from store.models import Product, Category
from orders.models import Order
from accounts.models import Membership 

def is_admin(u): return u.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'custom_admin/dashboard.html', {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='Pending').count(),
        'total_revenue': Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'recent_orders': Order.objects.all().order_by('-created_at')[:5]
    })

@user_passes_test(is_admin)
def admin_all_orders(request):
    q = request.GET.get('q')
    orders = Order.objects.all().order_by('-created_at')
    if q:
        orders = orders.filter(Q(id__icontains=q)|Q(first_name__icontains=q))
    return render(request, 'custom_admin/all_orders.html', {'orders': orders})

@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        if 'update_status' in request.POST:
            order.status = request.POST.get('status')
            order.save()
        elif 'update_address' in request.POST:
            order.address = request.POST.get('address')
            order.save()
        return redirect('admin_order_detail', order_id=order.id)
    return render(request, 'custom_admin/order_detail.html', {'order': order})

@user_passes_test(is_admin)
def admin_products_list(request):
    return render(request, 'custom_admin/products_list.html', {'products': Product.objects.all()})

@user_passes_test(is_admin)
def admin_add_product(request):
    if request.method == 'POST':
        p = Product.objects.create(
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            description=request.POST.get('description'),
            image=request.FILES.get('image')
        )
        p.categories.set(request.POST.getlist('categories'))
        p.save()
        return redirect('admin_products_list')
    return render(request, 'custom_admin/add_product.html', {'categories': Category.objects.all()})

@user_passes_test(is_admin)
def admin_edit_product(request, pid):
    p = get_object_or_404(Product, id=pid)
    if request.method == 'POST':
        p.name=request.POST.get('name')
        p.price=request.POST.get('price')
        p.save()
        return redirect('admin_products_list')
    return render(request, 'custom_admin/edit_product.html', {'product': p, 'categories': Category.objects.all()})

@user_passes_test(is_admin)
def admin_delete_product(request, pid):
    Product.objects.filter(id=pid).delete()
    return redirect('admin_products_list')

@user_passes_test(is_admin)
def admin_categories_list(request):
    return render(request, 'custom_admin/categories_list.html', {'categories': Category.objects.all()})

@user_passes_test(is_admin)
def admin_add_category(request):
    if request.method == 'POST':
        Category.objects.create(name=request.POST.get('name'), image=request.FILES.get('image'))
        return redirect('admin_categories_list')
    return render(request, 'custom_admin/add_category.html')

@user_passes_test(is_admin)
def admin_edit_category(request, cid):
    c = get_object_or_404(Category, id=cid)
    if request.method == 'POST':
        c.name=request.POST.get('name')
        c.save()
        return redirect('admin_categories_list')
    return render(request, 'custom_admin/edit_category.html', {'category': c})

@user_passes_test(is_admin)
def admin_delete_category(request, cid):
    Category.objects.filter(id=cid).delete()
    return redirect('admin_categories_list')

@user_passes_test(is_admin)
def admin_users(request):
    return render(request, 'custom_admin/users.html', {'users': User.objects.all()})

@user_passes_test(is_admin)
def admin_memberships(request):
    return render(request, 'custom_admin/memberships.html', {'members': Membership.objects.all()})