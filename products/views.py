"""
Views for the Products & Catalog module.

Uses class-based views for consistency and extensibility.
All heavy logic is delegated to ``services.py``.
"""
from django.views.generic import DetailView, ListView

from .models import Category, Product
from .services import filter_products, get_base_queryset, search_products


class ProductListView(ListView):
    """
    Display a paginated, filterable, searchable product catalogue.

    Supports query parameters:
        ?search=        — search by name / brand
        ?category=      — filter by category slug
        ?brand=         — filter by brand (partial match)
        ?min_price=     — minimum price
        ?max_price=     — maximum price
        ?volume=        — exact volume in ml
    """

    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Build queryset from service layer based on GET params."""
        params = self.request.GET
        search_query = params.get('search', '').strip()

        if search_query:
            queryset = search_products(search_query)
        else:
            queryset = get_base_queryset()

        return filter_products(
            queryset,
            category_slug=params.get('category'),
            brand=params.get('brand'),
            min_price=params.get('min_price'),
            max_price=params.get('max_price'),
            volume=params.get('volume'),
        )

    def get_context_data(self, **kwargs):
        """Inject categories and active filters into template context."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'brand': self.request.GET.get('brand', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'volume': self.request.GET.get('volume', ''),
        }
        return context


class ProductDetailView(DetailView):
    """Display full details for a single product."""

    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Use select_related to avoid extra queries on the detail page."""
        return get_base_queryset()
