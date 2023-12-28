from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from .models import Product, ReviewRating
from category.models import *
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import  messages
from orders.models import OrderProduct

# Create your views here.

def search(request):
    if request.GET.get('keywords'):
        products = Product.objects.all()
        keywords = request.GET.get('keywords')
        products = products.order_by('-created_at').filter(
                                    Q(product_name__icontains=keywords) | 
                                    Q(description__icontains = keywords )|
                                    Q(slug__icontains = keywords )
                                    )
        count = products.count()
    else:
        products = None
        count = 0

    return render(request, 'front/store/store.html', context={'products': products, 'count': count})
def store(request, category_slug=None):
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products  = Product.objects.all().filter(is_available=True).order_by('id')
        
    count = products.count()
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'front/store/store.html', context={'products': products, 'count':count})

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    if  request.user.is_authenticated:
        try:
            orderProduct = OrderProduct.objects.filter(user= request.user, product_id = single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderProduct = None
    else:
        orderProduct = None

    #   get reviews   
    reviews = ReviewRating.objects.filter(product__id = single_product.id, status=True)                                                                                                                                                                                               

    context={
        'single_product': single_product, 
        'in_cart': in_cart, 
        'reviews':reviews,
        'orderProduct': orderProduct,
        }
    return render(request, 'front/store/product_detail.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            if reviews:
                reviews.subject = request.POST.get('subject')
                reviews.rating = request.POST.get('rating')
                reviews.review = request.POST.get('review')
                reviews.ip = request.META.get('REMOTE_ADDR')
                reviews.save()
            messages.success(request, 'Thank your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            review = ReviewRating.objects.create(
                product_id = product_id,
                user_id = request.user.id,
                subject = request.POST.get('subject'),
                review = request.POST.get('review'),
                rating = request.POST.get('rating'),
                ip = request.META.get('REMOTE_ADDR'),
            )
            review.save()  
            messages.success(request, 'Thank your review has been submited.')
            return redirect(url)