"""
Тести для сервісів та бізнес-логіки додатку orders.
"""
from decimal import Decimal

import pytest
from django.http import HttpRequest

from orders.cart import Cart
from products.models import Product

@pytest.mark.django_db
class TestCart:
    """Тестування класу Cart (робота з кошиком)."""
    
    def test_cart_initialization(self, active_client):
        """Перевіряє, що кошик створюється порожнім."""
        request = HttpRequest()
        request.session = active_client.session
        cart = Cart(request)
        
        assert len(cart) == 0
        assert cart.get_total_price() == Decimal('0.00')

    def test_cart_add_and_total_price(self, active_client, product: Product):
        """Перевіряє додавання товару та підрахунок загальної суми."""
        request = HttpRequest()
        request.session = active_client.session
        cart = Cart(request)

        # Додаємо товар
        cart.add(product=product, quantity=2)
        assert len(cart) == 2
        
        expected_total = product.price * 2
        assert cart.get_total_price() == expected_total

        # Оновлюємо кількість (override)
        cart.add(product=product, quantity=5, override_quantity=True)
        assert len(cart) == 5
        
        expected_total_override = product.price * 5
        assert cart.get_total_price() == expected_total_override
        
    def test_cart_remove(self, active_client, product: Product):
        """Перевіряє видалення товару з кошика."""
        request = HttpRequest()
        request.session = active_client.session
        cart = Cart(request)

        cart.add(product=product, quantity=1)
        assert len(cart) == 1
        
        cart.remove(product)
        assert len(cart) == 0

    def test_cart_clear(self, active_client, product: Product):
        """Перевіряє повне очищення кошика."""
        request = HttpRequest()
        request.session = active_client.session
        cart = Cart(request)

        cart.add(product=product, quantity=3)
        cart.clear()
        
        assert len(cart) == 0
