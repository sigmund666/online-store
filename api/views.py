from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from store.models import Category, Product, CartItem, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer
)

# API для категорий
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# API для товаров
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по категории
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

# API для корзины
class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def get_session_id(self, request):
        # Получаем или создаём ID сессии для неавторизованного пользователя
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        return session_id
    
    def list(self, request):
        # Получить все товары в корзине
        session_id = self.get_session_id(request)
        cart_items = CartItem.objects.filter(session_id=session_id)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        # Добавить товар в корзину
        session_id = self.get_session_id(request)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        cart_item, created = CartItem.objects.get_or_create(
            session_id=session_id,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        # Удалить товар из корзины
        session_id = self.get_session_id(request)
        cart_item = get_object_or_404(CartItem, id=pk, session_id=session_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['put'])
    def update_quantity(self, request):
        # Обновить количество товара
        session_id = self.get_session_id(request)
        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        
        cart_item = get_object_or_404(CartItem, id=cart_item_id, session_id=session_id)
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        # Очистить всю корзину
        session_id = self.get_session_id(request)
        CartItem.objects.filter(session_id=session_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API для заказов
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # Если пользователь авторизован — показываем его заказы
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        # Если не авторизован — показываем заказы по сессии (упрощённо)
        return Order.objects.none()
    
    def create(self, request):
        # Создать новый заказ
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Получаем корзину
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            
            cart_items = CartItem.objects.filter(session_id=session_id)
            
            if not cart_items.exists():
                return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Создаём заказ
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=serializer.validated_data['full_name'],
                phone=serializer.validated_data['phone'],
                address=serializer.validated_data['address'],
                comment=serializer.validated_data.get('comment', ''),
                total_amount=0
            )
            
            total = 0
            # Создаём позиции заказа
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price
                )
                total += cart_item.product.price * cart_item.quantity
            
            order.total_amount = total
            order.save()
            
            # Очищаем корзину
            cart_items.delete()
            
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)