from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index_page'),
    path('list/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('auth/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('create/', views.create_order, name='create_order'),
    path('klient/', views.client_dashboard, name='client_dashboard'),
    path('zakaz/', views.order_history, name='order_history'),
    path('spisok/', views.product_admin_list, name='product_admin_list'),
    path('admin-page/', views.admin_dashboard, name='admin_dashboard'),
]
