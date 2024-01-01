from django.contrib import admin
from django.urls import path
from .views import Index, store, Signup, Login, logout, CheckOut, OrderView
# from .middlewares import auth_middleware  # Update the import path

urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('store', store, name='store'),

    path('signup', Signup.as_view(), name='signup'),
    path('login', Login.as_view(), name='login'),
    path('logout', logout, name='logout'),
    # path('cart', auth_middleware(Cart.as_view()), name='cart'),
    # path('check-out', auth_middleware(CheckOut.as_view()), name='checkout'),
    # path('orders', auth_middleware(OrderView.as_view()), name='orders'),
]
