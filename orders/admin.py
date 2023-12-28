from django.contrib import admin
from .models import *
# Register your models here.



admin.site.register(Payment)
class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    extra = 0
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'email', 'country', 'city', 
                  'state', 'order_note', 'tax', 'order_total', 'is_order', 'created_at']
    list_filter = ['is_order', 'status']
    search_fields = ['order_number', 'first_name','last_name','phone_number','email']
    list_per_page = 20
    inlines = [OrderProductInLine]
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)