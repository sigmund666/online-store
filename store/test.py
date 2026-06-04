from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, Product

class ProductTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Компьютеры")
        self.product = Product.objects.create(
            name="Ноутбук Lenovo",
            description="Мощный ноутбук",
            price=2000.00,
            stock=15,
            category=self.category,
            is_active=True
        )

    def test_get_products_list(self):
        url = '/api/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_detail(self):
        url = f'/api/products/{self.product.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        # 1. Добавляем товар в корзину
        cart_url = '/api/cart/'
        cart_data = {
            "product_id": self.product.id,
            "quantity": 2
        }
        cart_response = self.client.post(cart_url, cart_data, format='json')
        self.assertEqual(cart_response.status_code, status.HTTP_201_CREATED)
        
        # 2. Оформляем заказ
        order_url = '/api/orders/'
        order_data = {
            "full_name": "Иванов Иван",
            "phone": "+375291234567",
            "address": "Минск, ул. Ленина, 1"
        }
        order_response = self.client.post(order_url, order_data, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)


class CategoryTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Газонокосилки")

    def test_get_categories(self):
        url = '/api/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CartTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Компьютеры")
        self.product = Product.objects.create(
            name="Мышь Logitech",
            description="Беспроводная мышь",
            price=45.00,
            stock=30,
            category=self.category,
            is_active=True
        )

    def test_add_to_cart(self):
        url = '/api/cart/'
        data = {
            "product_id": self.product.id,
            "quantity": 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)