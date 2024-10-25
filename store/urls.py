from django.contrib import admin
from django.urls import path
from .views.home import Index
from .views.home import  store,HomePage
from .views.signup import Signup
from .views.login import Login , logout
from .views.cart import Cart, RemoveFromCart
from .views.checkout import CheckOut, payment_success
from .views.orders import OrderView
from .middlewares.auth import  auth_middleware
from .views.home import ProductDetail, PlanterDetail, ContactView

urlpatterns = [
    path('', HomePage.as_view(), name='home'),  # Homepage route
    path('store/', store, name='store'),
    path('signup', Signup.as_view(), name='signup'),
    path('login', Login.as_view(), name='login'),
    path('logout', logout , name='logout'),
    path('cart/', auth_middleware(Cart.as_view()) , name='cart'),
    path('check-out', CheckOut.as_view() , name='checkout'),
    path('payment-success', payment_success, name='payment_success'),
    path('orders', auth_middleware(OrderView.as_view()), name='orders'),
    path('product/<int:product_id>/', ProductDetail.as_view(), name='product_detail'),
    path('planter/<int:planter_id>/', PlanterDetail.as_view(), name='planter_detail'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('remove_from_cart/<str:item_key>/', RemoveFromCart.as_view(), name='remove_from_cart'),
]
