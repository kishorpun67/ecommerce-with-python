from django.shortcuts import render
from store.models import Product
# Create your views here.

def index(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_at');
    return render(request, 'front/index.html', context={'products': products})