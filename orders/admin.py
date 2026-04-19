"""
Django Admin configuration for the Orders module.

Provides a nested interface to manage Orders along with their items.
"""
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Allows editing order items directly inside the Order page."""
    
    model = OrderItem
    raw_id_fields = ['product']  # Полегшує вибір товару, якщо їх багато


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order management with detailed filtering."""

    list_display = (
        'id', 'first_name', 'last_name', 'email', 
        'address', 'city', 'paid', 'created'
    )
    list_filter = ('paid', 'created', 'updated')
    search_fields = ('first_name', 'last_name', 'email')
    inlines = [OrderItemInline]  # Відображення товарів у замовленні
    
    # Групування полів для кращого візувалу
    fieldsets = (
        ('Дані клієнта', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Доставка та статус', {
            'fields': ('address', 'city', 'paid')
        }),
    )
    