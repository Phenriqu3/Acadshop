from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Product, Cart, CartItem

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test description',
            short_description='Short desc',
            price=100.00,
            category=self.category,
            stock=10
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.category, self.category)

    def test_cart_creation(self):
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)

    def test_cart_item_creation(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.total_price, 200.00)