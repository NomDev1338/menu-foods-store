from django.shortcuts import render, redirect
from django.http import JsonResponse
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from store.models import Product, Category
from accounts.models import Membership
from .models import Order, OrderItem
import stripe

stripe.api_key = "_sktest" # Apni Stripe Key


def calculate_cart_totals(request, cart):
    subtotal = Decimal('0.00')
    items_count = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=pid)
            subtotal += p.price * qty
            items_count += qty
        except: continue
    
    delivery = Decimal('200.00')
    discount = Decimal('0.00')
    FREE_DELIVERY_THRESHOLD = Decimal('2500.00')
    shortfall = Decimal('0.00')

    # Logic
    if request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists():
        delivery = Decimal('0.00')
        discount = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
    
    elif subtotal >= FREE_DELIVERY_THRESHOLD:
        delivery = Decimal('0.00')
    
    else:
        # Calculate Shortfall for Non-Members
        if subtotal > 0:
            shortfall = FREE_DELIVERY_THRESHOLD - subtotal

    if items_count == 0:
        delivery = Decimal('0.00')
        shortfall = Decimal('0.00')
    
    grand_total = subtotal - discount + delivery
    
    # Return shortfall too
    return subtotal, delivery, discount, grand_total, items_count, shortfall

# --- CART ACTIONS ---

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'cart_count': sum(cart.values()), 'message': 'Item added!'})
    return redirect('cart_page')

def update_cart_action(request, product_id, action):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    
    if pid in cart:
        if action == 'increase': cart[pid] += 1
        elif action == 'decrease':
            if cart[pid] > 1: cart[pid] -= 1
            else: del cart[pid]
        elif action == 'remove': del cart[pid]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    # AJAX Response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Unpack updated return values (added shortfall)
        sub, delivery, disc, total, count, shortfall = calculate_cart_totals(request, cart)
        
        item_total = Decimal('0.00')
        item_qty = 0
        if pid in cart:
            p = Product.objects.get(id=pid)
            item_qty = cart[pid]
            item_total = p.price * item_qty
        
        return JsonResponse({
            'status': 'success',
            'cart_count': count,
            'subtotal': str(sub),
            'delivery': str(delivery),
            'discount': str(disc),
            'total': str(total),
            'shortfall': str(shortfall), # New data for frontend
            'item_qty': item_qty,
            'item_total': str(item_total)
        })
        
    return redirect('cart_page')

def increase_cart(request, product_id): return update_cart_action(request, product_id, 'increase')
def decrease_cart(request, product_id): return update_cart_action(request, product_id, 'decrease')
def remove_from_cart(request, product_id): return update_cart_action(request, product_id, 'remove')

# --- CART PAGE ---
def cart_page(request):
    cart = request.session.get('cart', {})
    items = []
    
    # Unpack updated return values
    sub, delivery, disc, total, count, shortfall = calculate_cart_totals(request, cart)
    
    is_member = False
    if request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists():
        is_member = True

    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=pid)
            items.append({'product': p, 'quantity': qty, 'total_price': p.price * qty})
        except: continue
        
    return render(request, 'orders/cart.html', {
        'cart_items': items,
        'subtotal': sub,
        'discount': disc,
        'delivery_fee': delivery,
        'grand_total': total,
        'is_member': is_member,
        'shortfall': shortfall,
        'categories': Category.objects.all()
    })

# --- CHECKOUT, SUCCESS, MY_ORDERS ---

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart: return redirect('home')
    
    sub, delivery, disc, total, count, shortfall = calculate_cart_totals(request, cart)
    
    is_member = False
    if request.user.is_authenticated and Membership.objects.filter(user=request.user, is_paid=True).exists():
        is_member = True

    if request.method == 'POST':
        method = request.POST.get('payment_method')
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'), last_name=request.POST.get('last_name'),
            email=request.POST.get('email'), phone=request.POST.get('phone'),
            address=request.POST.get('address'), city=request.POST.get('city'),
            payment_method=method, total_amount=total
        )
        for pid, qty in cart.items():
            OrderItem.objects.create(order=order, product=Product.objects.get(id=pid), price=Product.objects.get(id=pid).price, quantity=qty)
        
        if method == 'cod':
            request.session['cart'] = {}
            return redirect('success')
        else:
            YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
            try:
                s = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{'price_data': {'currency': 'pkr', 'unit_amount': int(total * 100), 'product_data': {'name': f'Order #{order.id}'}}, 'quantity': 1}],
                    mode='payment',
                    success_url=YOUR_DOMAIN + '/payments/success/',
                    cancel_url=YOUR_DOMAIN + '/payments/cancel/'
                )
                return redirect(s.url, code=303)
            except: pass

    return render(request, 'orders/checkout.html', {
        'total': sub,
        'discount': disc,
        'delivery_fee': delivery,
        'grand_total': total,
        'is_member': is_member,
        'categories': Category.objects.all()
    })

def success(request):
    return render(request, 'orders/success.html', {'categories': Category.objects.all()})

@login_required(login_url='login')
def my_orders(request):
    return render(request, 'orders/my_orders.html', {
        'orders': Order.objects.filter(user=request.user).order_by('-created_at'),
        'categories': Category.objects.all()
    })