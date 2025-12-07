from django.shortcuts import render
from store.models import Category

def success(request): 
    request.session['cart'] = {}
    return render(request, 'orders/success.html', {'categories': Category.objects.all()})

def cancel(request):
    return render(request, 'orders/cancel.html', {'categories': Category.objects.all()})