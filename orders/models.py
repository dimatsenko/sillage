"""
Models for the Orders module.

Defines Order and OrderItem entities for managing customer purchases
in the Sillage perfume decant store.
"""

from django.db import models
from products.models import Product

class Order(models.Model):
    """
    Stores general information about a customer's order.

    Fields:
        first_name, last_name, email — customer contact details.
        address, city — shipping information.
        paid — status flag to track payment.
    """

    first_name = models.CharField(max_length=50, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=50, verbose_name='Прізвище')
    email = models.EmailField(verbose_name='Email')
    address = models.CharField(max_length=250, verbose_name='Адреса')
    city = models.CharField(max_length=100, verbose_name='Місто')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated = models.DateTimeField(auto_now=True, verbose_name='Оновлено')
    paid = models.BooleanField(default=False, verbose_name='Оплачено')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

    def __str__(self):
        return f'Замовлення {self.id}'


class OrderItem(models.Model):
    """
    A specific product item within an order.

    Links a Product to an Order, capturing the price at the moment 
    of purchase to ensure historical accuracy.
    """
    
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Замовлення')
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name='Товар')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')

    def __str__(self):
        return str(self.id)
