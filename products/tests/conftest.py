"""
Shared pytest fixtures for the Products test suite.

Provides reusable Category and Product instances so individual test
modules stay DRY.
"""
import pytest

from products.models import Category, Product


@pytest.fixture
def category(db) -> Category:
    """Return a persisted Category instance."""
    return Category.objects.create(name='Нішева парфумерія', slug='nisheva')


@pytest.fixture
def another_category(db) -> Category:
    """Return a second Category for multi-category tests."""
    return Category.objects.create(name='Арабська парфумерія', slug='arabska')


@pytest.fixture
def product(db, category) -> Product:
    """Return a persisted Product instance linked to the default category."""
    return Product.objects.create(
        name='Aventus',
        brand='Creed',
        description='Культовий чоловічий аромат з нотами ананаса та берези.',
        price='1250.00',
        volume=10,
        category=category,
    )


@pytest.fixture
def product_list(db, category, another_category) -> list[Product]:
    """Create a batch of products for filtering / search / pagination tests."""
    products = [
        Product(
            name='Aventus',
            brand='Creed',
            description='Культовий аромат',
            price='1250.00',
            volume=10,
            category=category,
        ),
        Product(
            name='Sauvage',
            brand='Dior',
            description='Свіжий та динамічний',
            price='950.00',
            volume=5,
            category=category,
        ),
        Product(
            name='Oud Wood',
            brand='Tom Ford',
            description='Деревний східний аромат',
            price='1800.00',
            volume=10,
            category=another_category,
        ),
        Product(
            name='Baccarat Rouge 540',
            brand='Maison Francis Kurkdjian',
            description='Розкішний аромат',
            price='2200.00',
            volume=2,
            category=another_category,
        ),
    ]
    return Product.objects.bulk_create(products)
