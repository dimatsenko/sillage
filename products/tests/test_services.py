"""
Unit tests for the products service layer (filtering and search).
"""
from decimal import Decimal

import pytest

from products.services import filter_products, search_products


@pytest.mark.usefixtures('product_list')
class TestFilterProducts:

    def test_no_filters_returns_all(self):
        """No arguments returns all products."""
        assert filter_products().count() == 4

    def test_filter_by_category(self, category):
        """Category slug filters correctly."""
        result = filter_products(category_slug=category.slug)
        assert result.count() == 2
        assert all(p.category == category for p in result)

    def test_filter_by_price_range(self):
        """Combined min/max price filters."""
        result = filter_products(min_price='1000', max_price='1500')
        assert result.count() == 1

    def test_combined_filters(self, category):
        """Multiple filters stack correctly."""
        result = filter_products(category_slug=category.slug, brand='Creed', volume='10')
        assert result.count() == 1
        assert result.first().name == 'Aventus'

    def test_invalid_price_ignored(self):
        """Non-numeric price does not crash."""
        assert filter_products(min_price='abc').count() == 4


@pytest.mark.usefixtures('product_list')
class TestSearchProducts:

    def test_search_by_name(self):
        """Search by product name."""
        result = search_products('aventus')
        assert result.count() == 1
        assert result.first().name == 'Aventus'

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        assert search_products('DIOR').count() == 1

    def test_empty_search_returns_none(self):
        """Blank string returns empty queryset."""
        assert search_products('').count() == 0
