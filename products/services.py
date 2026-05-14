"""
Business-logic services for the Products module.

Encapsulates filtering and search logic, keeping views thin.
Follows SOLID principles:
- SRP: Each function has one clear responsibility.
- OCP: filter_products is extensible via keyword arguments.
"""
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from django.db.models import Max, Min, Q, QuerySet

from .models import Product


def get_base_queryset() -> QuerySet[Product]:
    """
    Return the base Product queryset with related Category pre-loaded.
    """
    return Product.objects.select_related('category')


def filter_products(
    queryset: Optional[QuerySet[Product]] = None,
    **filters: Any
) -> QuerySet[Product]:
    """
    Apply catalogue filters to a Product queryset.

    Accepts arbitrary filters to remain open for extension without
    modifying the core logic for every new field.
    """
    if queryset is None:
        queryset = get_base_queryset()

    # Category filter
    category_slug = filters.get('category_slug')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    # Brand filters (supports multiple and single)
    brands = filters.get('brands')
    brand = filters.get('brand')
    if brands:
        queryset = queryset.filter(brand__in=brands)
    elif brand:
        queryset = queryset.filter(brand__icontains=brand)

    # Simple exact matches
    for field in ['gender', 'fragrance_group']:
        val = filters.get(field)
        if val:
            queryset = queryset.filter(**{field: val})

    # Numeric range filters
    queryset = _apply_numeric_filter(queryset, 'price__gte', filters.get('min_price'), Decimal)
    queryset = _apply_numeric_filter(queryset, 'price__lte', filters.get('max_price'), Decimal)
    queryset = _apply_numeric_filter(queryset, 'volume', filters.get('volume'), int)

    return queryset


def search_products(
    query: str,
    queryset: Optional[QuerySet[Product]] = None,
    limit: Optional[int] = None
) -> QuerySet[Product]:
    """
    Full-text search across product name and brand.
    """
    if queryset is None:
        queryset = get_base_queryset()

    cleaned = query.strip()
    if not cleaned:
        return queryset.none()

    qs = queryset.filter(
        Q(name__icontains=cleaned) | Q(brand__icontains=cleaned)
    )
    
    if limit:
        qs = qs[:limit]
        
    return qs


def get_catalog_stats() -> dict[str, Any]:
    """
    Aggregate statistics for the catalog filters (e.g. price range).
    """
    stats = Product.objects.aggregate(
        min_p=Min('price'), 
        max_p=Max('price')
    )
    return {
        'min_price': int(stats['min_p'] or 0),
        'max_price': int(stats['max_p'] or 0),
    }


def _apply_numeric_filter(queryset: QuerySet, field_lookup: str, value: Any, type_factory: type) -> QuerySet:
    """Helper to apply numeric filters safely."""
    if value:
        try:
            return queryset.filter(**{field_lookup: type_factory(value)})
        except (InvalidOperation, ValueError, TypeError):
            pass
    return queryset
