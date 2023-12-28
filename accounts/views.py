from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .form import RegisterForm
from .models import *
from django.contrib import  messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.db import transaction
from carts.models import *
from carts.views import _cart_id
import requests
from orders.models import Order, OrderProduct
# Create your views here.

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists =  CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    # return HttpResponse(cart_item)
                    # gettting the product variation by cart id 
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    
                    # Get the cart items from the user to access his product variantions 
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            user = Account.objects.get(email=user.email)    
                            item.user =user,
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user= user
                                item.save()
            except Exception as e:
                pass
            login(request, user)
            
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                # return HttpResponse(params['next'])
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                pass
            return redirect('dashboard')
        else:
            messages.warning(request, 'Invalid email or password !')
    return render(request, 'front/accounts/login.html')

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        # if form.is_valid():
        # return HttpResponse(form.cleaned_data['first_name'])
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email') 
        password = request.POST.get('password')
        username = email.split('@')[0]
        user = Account.objects.create_user(first_name,last_name, email, username, password)
        user.phone_number = phone_number
        user.save()
        
        current_site = get_current_site(request)
        mail_subject = 'Pleas activate your account'
        message = render_to_string('email/account_verification.html', { 
                                                           'user': user, 
                                                            'domain': current_site, 
                                                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),                                                           
                                                            'token': default_token_generator.make_token(user)
                                                           })
        to_email = email
        send_email = EmailMessage(mail_subject, to = [to_email])
        send_email.send()
        
        # messages.success(request, "Thank you fror registering with us. We have sent you a verificsaton email addres. Pleas verify it.")
        return redirect('/user/login/?command=verification&email='+email)
    else :       
        form = RegisterForm
    context = {
        'form': form,
    }
    return render(request, 'front/accounts/register.html', context)

@login_required(login_url="login")
def user_logout(request):
    logout(request)
    messages.success(request, 'Logout successfully')
    return redirect(reverse('login'))

@login_required(login_url="login")
def dashboard(request):
    userProfile = get_object_or_404(UserProfile, user=request.user)
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_order = True)
    orders_count = orders.count()
    context = {
        'orders': orders,
        'orders_count': orders_count,
        'userProfile' : userProfile
    }
    return render(request, 'front/accounts/dashboard.html', context)

def activate(request, uid, token):
    try: 
        uid = urlsafe_base64_decode(uid)
        user  = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError,  Account.DoesNotExisT):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated ')
        return redirect('login')
    else :
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
    
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Pleas Reset yor password'
            message = render_to_string('email/reset_password_email.html', { 
                                                            'user': user, 
                                                                'domain': current_site, 
                                                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),                                                           
                                                                'token': default_token_generator.make_token(user)
                                                            })
            to_email = email
            send_email = EmailMessage(mail_subject, to = [to_email])
            send_email.send()
            
            messages.success(request, 'Password reset email has been sent to your email')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    return render(request, 'front/accounts/forgotPassword.html')


def resetpassword_validate(request, uid, token):
    try: 
        uid = urlsafe_base64_decode(uid)
        user  = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError,  Account.DoesNotExisT):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] =uid
        messages.success(request, 'Please reset your password')
        return redirect('login')
    else :
        messages.error(request, 'This link has been expired')
        return redirect('resetPassword')
    
def resetPassword(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password changed successfully')
            return redirect('login')
        else:
            messages.error(request, 'Password dose not match')
            return redirect('resetPassword')
    return render(request, 'front/accounts/reset_password.html')

@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_order = True)
    context = {
        'orders': orders,
    }
    return render(request, 'front/accounts/my_orders.html', context)

def order_detail(request, order_number):
    order = Order.objects.get(order_number=order_number)
    orderProduct = OrderProduct.objects.filter(order_id = order.id)
    
    total = 0
    for item in orderProduct:
        total += item.quantity* item.product_price
    # return HttpResponse(orderProduct)
    context = {
        'order': order,
        'orderProduct': orderProduct,
        'total':total,
    }
    return render(request, 'front/accounts/order_detail.html', context)

def edit_profile(request):    
    userProfile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        state = request.POST.get('state')
        city = request.POST.get('city')
        country = request.POST.get('country')
        profile_picture = request.POST.get('profile_picture')
        
        account = Account.objects.get(id = request.user.id)
        account.first_name = first_name
        account.last_name = last_name
        account.phone_number = phone_number
        account.save()
        
        if userProfile:
            userProfile.address_line_1 = address_line_1
            userProfile.address_line_2 = address_line_2
            userProfile.state = state
            userProfile.city = city
            userProfile.country = country
            userProfile.save()
        else:

            profile = UserProfile.objects.create(
                user = request.user,
                address_line_1 = address_line_1,
                address_line_2 = address_line_2,
                state = state, 
                city = city, 
                country = country
            )
            if profile_picture:
                profile.profile_picture = profile_picture
            profile.save()
        messages.success(request, 'User profile updated successfully')
        return redirect('edit_profile')
    context = {
        'userProfile': userProfile
    }
    return render(request, 'front/accounts/edit_profile.html', context)


def change_password(request):
    if request.method == 'POST':
        try:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            user = Account.objects.get(username__exact=request.user.username)
            if new_password == confirm_password:
                success = user.check_password(current_password)
                if success:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password changed successfully')
                else:
                    messages.error(request, 'Current password is incorrect')
            else:
                messages.error(request, 'New Password and Confirm Password are incorrect')
        except Exception as e:
            pass       
        return redirect('change_password')
    return render(request, 'front/accounts/change_password.html')
