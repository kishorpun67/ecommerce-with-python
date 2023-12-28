from django.shortcuts import render, redirect, HttpResponse
from store.models import *
from carts.models import Cart, CartItem
from .forms import OrderForm
from .models import *
from datetime import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.



def payments(request, order_number):
    if order_number:
        order = Order.objects.get(user=request.user, is_order=False, order_number=order_number)
        # payment = 
        order.is_order = True
        order.save()
        
        # return HttpResponse(order.id)
        # get pdouct of items card and insert into productorder table
        cart_items = CartItem.objects.filter(user = request.user)
        
        for item in cart_items:
            orderProduct = OrderProduct()
            orderProduct.order_id = order.id
            orderProduct.user_id = request.user.id
            orderProduct.product_id = item.product_id
            orderProduct.quantity = item.quantity
            orderProduct.product_price = item.product.price
            orderProduct.ordered = True
            # orderProduct.variation =item.variations.all()
            orderProduct.save()
            
            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderProduct = OrderProduct.objects.get(id=orderProduct.id)
            # return HttpResponse(orderProduct)
            orderProduct.variation.set(product_variation)
            orderProduct.save()
            
            
            # reduce quantity  from product 
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()
         
        CartItem.objects.filter(user=request.user).delete()   
        
        # mail send to user 
        mail_subject = 'Thank you for your order!'
        message = render_to_string('email/order_recive_email.html', { 
                                                           'user': request.user,
                                                           'order': order, 
                                                        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, to = [to_email])
        send_email.send()
        return redirect('order_complete', order_number = order.order_number)
    return render(request, 'front/orders/payments.html')

def order_complete(request, order_number):
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
    return render(request, 'front/orders/order_complete.html', context)

def place_order(request, total=0, quantity=0, cart_items=None):
    current_user = request.user
    cart_items =  CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('checkout')
    
    if request.method == "POST":
        try:
            form = OrderForm(request.POST)
            tax = 0                     
            grand_total = 0
            for  item in cart_items:
                total += (item.product.price * item.quantity)
                quantity += item.quantity
            tax =(2*total)/100
            grand_total = total + tax
            # if form.is_valid():
                # store all the data billing information inside oder table 
            data = Order()
            data.user = current_user
            data.first_name = request.POST["first_name"]
            data.last_name = request.POST["last_name"]
            data.phone_number = request.POST["phone_number"]
            data.email = request.POST["email"]
            data.address_line_1 = request.POST["address_line_1"]
            data.address_line_2 = request.POST["address_line_2"]
            data.country = request.POST["country"]
            data.state = request.POST["state"]
            data.city = request.POST["city"]
            data.country = request.POST["country"]
            data.order_note = request.POST["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            # Generate Oder Number 
            # yr = int(datetime.date.today().strftime('%y'))
            # dt = int(datetime.date.today().strftime('%d'))
            # mt = int(datetime.date.today().strftime('%m'))
            # d = datetime(yr, mt, dt)
            # current_time = d.strftime('%Y-%m-%d')
            now = datetime.now()
            current_time = now.strftime('%Y-%m-%d')
            order_number = current_time + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_order=False, order_number=order_number)
            context ={
                'order': order,
                'cart_items': cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request, 'front/orders/payments.html', context)
        except Exception as e:
            raise e
            
    
    