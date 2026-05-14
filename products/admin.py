"""
Django Admin configuration for the Products module.

Provides full CRUD with search, filtering, and optimised list views
for Category and Product models.
"""
from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category management."""

    list_display = ('name', 'slug', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    @admin.display(description='Кількість товарів')
    def product_count(self, obj: Category) -> int:
        """Return the number of products in this category."""
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product management."""

    list_display = (
        'name',
        'brand',
        'category',
        'gender',
        'fragrance_group',
        'price',
        'volume',
        'image',
    )
    list_filter = ('category', 'brand', 'gender', 'fragrance_group', 'volume')
    search_fields = ('name', 'brand', 'description')
    list_select_related = ('category',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'brand', 'category', 'gender'),
        }),
        ('Характеристики', {
            'fields': ('price', 'volume', 'fragrance_group', 'image', 'description'),
        }),
        ('Службова інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
