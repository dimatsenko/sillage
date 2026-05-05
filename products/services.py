"""
Business-logic services for the Products module.

Encapsulates filtering and search logic, keeping views thin.
All querysets returned use select_related for FK optimisation.
"""
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.db.models import Q, QuerySet

from .models import Product


def get_base_queryset() -> QuerySet[Product]:
    """
    Return the base Product queryset with related Category pre-loaded.

    Every public query should originate from this function to guarantee
    consistent select_related usage and avoid N+1 problems.
    """
    return Product.objects.select_related('category')


def filter_products(
    queryset: Optional[QuerySet[Product]] = None,
    *,
    category_slug: Optional[str] = None,
    brand: Optional[str] = None,
    brands: Optional[list[str]] = None,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    volume: Optional[str] = None,
    gender: Optional[str] = None,
    fragrance_group: Optional[str] = None,
) -> QuerySet[Product]:
    """
    Apply catalogue filters to a Product queryset.

    Args:
        queryset:      Starting queryset (defaults to ``get_base_queryset``).
        category_slug: Exact match on ``category.slug``.
        brand:         Case-insensitive containment match on ``brand``.
        min_price:     Minimum price (inclusive).
        max_price:     Maximum price (inclusive).
        volume:        Exact match on ``volume`` (ml).

    Returns:
        Filtered queryset.  Invalid numeric values are silently ignored
        to prevent 400 errors from user-supplied query strings.
    """
    if queryset is None:
        queryset = get_base_queryset()

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    if brands:
        queryset = queryset.filter(brand__in=brands)
    elif brand:
        queryset = queryset.filter(brand__icontains=brand)

    if gender:
        queryset = queryset.filter(gender=gender)

    if fragrance_group:
        queryset = queryset.filter(fragrance_group=fragrance_group)

    if min_price is not None:
        try:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        except (InvalidOperation, ValueError):
            pass  # ignore invalid input

    if max_price is not None:
        try:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        except (InvalidOperation, ValueError):
            pass  # ignore invalid input

    if volume is not None:
        try:
            queryset = queryset.filter(volume=int(volume))
        except (ValueError, TypeError):
            pass  # ignore invalid input

    return queryset


def search_products(
    query: str,
    queryset: Optional[QuerySet[Product]] = None,
) -> QuerySet[Product]:
    """
    Full-text search across product name and brand.

    Uses case-insensitive containment (``icontains``) which is portable
    across SQLite and PostgreSQL without extra extensions.

    Args:
        query:    Search string entered by the user.
        queryset: Starting queryset (defaults to ``get_base_queryset``).

    Returns:
        Filtered queryset matching the search term.
        Returns an empty queryset if the search string is blank.
    """
    if queryset is None:
        queryset = get_base_queryset()

    cleaned = query.strip()
    if not cleaned:
        return queryset.none()

    return queryset.filter(
        Q(name__icontains=cleaned) | Q(brand__icontains=cleaned)
    )
