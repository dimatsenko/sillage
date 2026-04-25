"""
Integration tests for Product views (list + detail).
"""
import pytest
from django.urls import reverse

from products.models import Product


@pytest.mark.usefixtures('product_list')
class TestProductListView:

    def test_list_returns_200(self, client):
        """GET /products/ returns HTTP 200."""
        response = client.get(reverse('products:list'))
        assert response.status_code == 200

    def test_filter_by_category(self, client, category):
        """?category=<slug> filters the product list."""
        response = client.get(reverse('products:list'), {'category': category.slug})
        assert all(p.category == category for p in response.context['products'])

    def test_search(self, client):
        """?search=<term> searches by name/brand."""
        response = client.get(reverse('products:list'), {'search': 'Sauvage'})
        assert response.context['products'].count() == 1


class TestProductDetailView:

    def test_detail_returns_200(self, client, product):
        """GET /products/<pk>/ returns HTTP 200."""
        response = client.get(reverse('products:detail', kwargs={'pk': product.pk}))
        assert response.status_code == 200

    def test_detail_404(self, client, db):
        """Non-existent product returns 404."""
        response = client.get(reverse('products:detail', kwargs={'pk': 99999}))
        assert response.status_code == 404
