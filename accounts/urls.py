from django.urls import path
from .views import *
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    # path('dashboard/', dashboard, name='dashboard'),
    path('activate/<str:uid64>/<str:token>/', activate, name='activate'),
    path('forgotPassword/', forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<str:uid64>/<str:token>/', resetpassword_validate, name='resetpassword'),
    path('resetPassword/', resetPassword, name='resetPassword'),
    
    path('my_orders/', my_orders, name='my_orders'),
    path('order_detail/<order_number>', order_detail, name='order_detail'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('change_password/', change_password, name='change_password'),
    
    
    
    
    
    
]