"""
Тести для моделей додатку orders.
"""
import pytest
from orders.models import Order, OrderItem
from products.models import Product

@pytest.mark.django_db
class TestOrderModels:
    """Тестування моделей Order та OrderItem."""
    
    def test_order_str(self):
        """Перевіряє рядкове представлення моделі Order."""
        order = Order.objects.create(
            first_name="Тест",
            last_name="Тестов",
            email="test@example.com",
            address="Адреса",
            city="Місто"
        )
        assert str(order) == f"Замовлення {order.id}"

    def test_order_item_str(self, product: Product):
        """Перевіряє рядкове представлення моделі OrderItem."""
        order = Order.objects.create(
            first_name="Тест",
            last_name="Тестов",
            email="test@example.com",
            address="Адреса",
            city="Місто"
        )
        item = OrderItem.objects.create(
            order=order,
            product=product,
            price=product.price,
            quantity=1
        )
        assert str(item) == str(item.id)
