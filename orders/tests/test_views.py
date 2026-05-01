"""
Інтеграційні тести для представлень (views) додатку orders.
"""
import pytest
from django.conf import settings
from django.urls import reverse

from orders.models import Order, OrderItem
from products.models import Product

@pytest.mark.django_db
class TestCartViews:
    """Тестування маршрутів для роботи з кошиком."""
    
    @pytest.mark.parametrize("quantity, override, expected_quantity", [
        (1, False, 1),
        (5, False, 5),
        (10, True, 10),
    ])
    def test_cart_add_view_parameterized(
        self, active_client, product: Product, quantity: int, override: bool, expected_quantity: int
    ):
        """POST /cart/add/<id>/ додає товар у кошик та перенаправляє."""
        url = reverse('orders:cart_add', args=[product.id])
        data = {'quantity': quantity, 'override': override}
        
        response = active_client.post(url, data=data)
        
        assert response.status_code == 302
        assert response.url == reverse('orders:cart_detail')
        
        session_cart = active_client.session.get(settings.CART_SESSION_ID)
        assert session_cart is not None
        assert str(product.id) in session_cart
        assert session_cart[str(product.id)]['quantity'] == expected_quantity
        
    def test_cart_remove_view(self, active_client, product: Product):
        """POST /cart/remove/<id>/ видаляє товар з кошика."""
        add_url = reverse('orders:cart_add', args=[product.id])
        active_client.post(add_url, data={'quantity': 1, 'override': False})
        
        remove_url = reverse('orders:cart_remove', args=[product.id])
        response = active_client.post(remove_url)
        
        assert response.status_code == 302
        assert response.url == reverse('orders:cart_detail')
        
        session_cart = active_client.session.get(settings.CART_SESSION_ID)
        assert str(product.id) not in session_cart

    def test_cart_detail_view(self, active_client, product: Product):
        """GET /cart/ повертає сторінку кошика (HTTP 200)."""
        active_client.post(reverse('orders:cart_add', args=[product.id]), data={'quantity': 1})
        response = active_client.get(reverse('orders:cart_detail'))
        
        assert response.status_code == 200


@pytest.mark.django_db
class TestOrderViews:
    """Тестування маршрутів оформлення замовлення."""
    
    def test_order_create_get(self, client):
        """GET /create/ повертає форму оформлення замовлення."""
        response = client.get(reverse('orders:order_create'))
        assert response.status_code == 200

    def test_order_create_post_success(self, active_client, product: Product):
        """POST /create/ з валідними даними створює замовлення і очищує кошик."""
        active_client.post(reverse('orders:cart_add', args=[product.id]), data={'quantity': 2})
        
        url = reverse('orders:order_create')
        form_data = {
            'first_name': 'Іван',
            'last_name': 'Іванов',
            'email': 'ivan@example.com',
            'address': 'Вул. Тестова, 1',
            'city': 'Київ'
        }
        
        response = active_client.post(url, data=form_data)
        
        assert response.status_code == 200
        
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.email == 'ivan@example.com'
        
        assert OrderItem.objects.count() == 1
        item = OrderItem.objects.first()
        assert item.order == order
        assert item.product == product
        assert item.quantity == 2
        
        session_cart = active_client.session.get(settings.CART_SESSION_ID)
        assert not session_cart
