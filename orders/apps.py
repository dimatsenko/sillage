"""Django app configuration for the Orders module."""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the Orders & Cart application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Замовлення та кошик'
    