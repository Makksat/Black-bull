from django.urls import path
#login funcionality 
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views




urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    
	path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    
	path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
	path('product/<int:pk>/', views.product_detail, name="product_detail"),
    
]