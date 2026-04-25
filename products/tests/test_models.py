"""
Unit tests for Category and Product models.
"""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from products.models import Category, Product


class TestCategoryModel:

    def test_create_category(self, category):
        """Category is persisted with correct field values."""
        assert category.pk is not None
        assert category.name == 'Нішева парфумерія'
        assert category.slug == 'nisheva'

    def test_unique_slug_constraint(self, category, db):
        """Duplicate slug raises IntegrityError."""
        with pytest.raises(IntegrityError):
            Category.objects.create(name='Інша категорія', slug='nisheva')


class TestProductModel:

    def test_create_product(self, product):
        """Product is persisted with correct field values."""
        assert product.pk is not None
        assert product.name == 'Aventus'
        assert product.brand == 'Creed'
        assert Decimal(str(product.price)) == Decimal('1250.00')

    def test_get_absolute_url(self, product):
        """get_absolute_url returns the correct detail path."""
        assert product.get_absolute_url() == f'/products/{product.pk}/'

    def test_price_minimum_validation(self, category, db):
        """Price below 0.01 must fail validation."""
        p = Product(name='Test', brand='Test', price=Decimal('0.00'),
                    volume=5, category=category)
        with pytest.raises(ValidationError):
            p.full_clean()

    def test_protect_category_deletion(self, product):
        """Deleting a category with products raises ProtectedError."""
        from django.db.models import ProtectedError
        with pytest.raises(ProtectedError):
            product.category.delete()
