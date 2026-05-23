from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаём роутер (автоматически создаёт все URL)
router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('cart', views.CartViewSet, basename='cart')
router.register('orders', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]