"""Django app configuration for the Products module."""
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Configuration for the Products & Catalog application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = 'Товари та каталог'
