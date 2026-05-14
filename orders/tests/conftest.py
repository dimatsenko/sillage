"""
Спільні фікстури для тестів додатку orders.
"""
from decimal import Decimal
import pytest
from django.conf import settings
from django.test import Client

from products.models import Category, Product

@pytest.fixture
def category() -> Category:
    """Фікстура для створення тестової категорії."""
    return Category.objects.create(
        name="Тестова категорія",
        slug="test-category"
    )

@pytest.fixture
def product(category: Category) -> Product:
    """Фікстура для створення тестового товару."""
    return Product.objects.create(
        category=category,
        name="Тестовий парфум",
        brand="Test Brand",
        price=Decimal('1500.00'),
        volume=50,
        description="Опис тестового товару"
    )

@pytest.fixture
def active_client(client: Client) -> Client:
    """
    Фікстура, що налаштовує клієнта з активною сесією.
    Ініціалізує порожній кошик у сесії для уникнення KeyError при старті.
    """
    session = client.session
    session[settings.CART_SESSION_ID] = {}
    session.save()
    return client