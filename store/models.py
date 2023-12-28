from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import *

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True, help_text="Name of the product")
    slug = models.SlugField(max_length=200 , unique=True, help_text="Slug of the product")
    description = models.TextField(blank=True, null=True, help_text="Description of the product")
    price = models.DecimalField(max_digits=5, decimal_places=2, help_text="Price of the product")
    images = models.ImageField(upload_to='photos/products/', help_text="Image of the product")
    stock = models.IntegerField(null=True, help_text="Stock of the product")
    is_available = models.BooleanField(default=True, null=True, help_text="Availability of the product")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text="Category of the product")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product_name
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    class Meta:
        ordering = ('-id',)
        verbose_name = 'product'
        verbose_name_plural = 'products'
    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=(
    ('color', 'color'),
    ('size', 'size'),))
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
    def __str__(self):
        return self.variation_value
    objects = VariationManager()
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True, null=True)
    review = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str_(self):
        return self.subject
