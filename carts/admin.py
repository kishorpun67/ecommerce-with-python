from django.contrib import admin
from .models import *
# Register your models here .


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'created_at')
admin.site.register(Cart, CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'is_active')
admin.site.register(CartItem, CartItemAdmin)
