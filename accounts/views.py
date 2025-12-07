from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm, MembershipSignupForm
from .models import Membership
from store.models import Category
import stripe

stripe.api_key = "_sktest" 

# --- AUTHENTICATION ---

def login_view(request):
    if request.method == 'POST':
        u = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if u: 
            login(request, u)
            return redirect('home')
        messages.error(request, "Invalid credentials")
    return render(request, 'accounts/login.html', {'categories': Category.objects.all()})


def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            u.username = form.cleaned_data['email'].split('@')[0]
            u.set_password(form.cleaned_data['password'])
            u.save()
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'categories': Category.objects.all()})



def membership_signup(request):
    FEE = 2000
    if request.method == 'POST':
        form = MembershipSignupForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                u = User.objects.create_user(username=data['email'].split('@')[0], email=data['email'], password=data['password'])
                u.first_name = data['first_name']; u.last_name = data['last_name']; u.save()
                
                Membership.objects.create(user=u, phone=data['phone'], is_paid=False, amount_paid=FEE)
                login(request, u, backend='django.contrib.auth.backends.ModelBackend')
                
                YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
                s = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{'price_data': {'currency': 'pkr', 'unit_amount': FEE*100, 'product_data': {'name': 'Premium Membership'}}, 'quantity': 1}],
                    mode='payment', success_url=YOUR_DOMAIN + '/auth/membership-success/', cancel_url=YOUR_DOMAIN + '/payments/cancel/'
                )
                return redirect(s.url, code=303)
            except Exception as e: messages.error(request, str(e))
    else:
        form = MembershipSignupForm()
    return render(request, 'accounts/membership.html', {'form': form, 'categories': Category.objects.all()})

def membership_success(request):
    if request.user.is_authenticated:
        try: 
            m = Membership.objects.get(user=request.user)
            m.is_paid = True
            m.save()
        except: pass
    return render(request, 'accounts/welcome_member.html', {'categories': Category.objects.all()})