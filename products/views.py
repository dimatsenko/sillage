"""
Views for the Products & Catalog module.

Uses class-based views for consistency and extensibility.
All heavy logic is delegated to ``services.py``.
"""
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, TemplateView

from .models import Category, Product
from .services import filter_products, get_base_queryset, search_products, get_catalog_stats
from orders.forms import CartAddProductForm


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 4 найновіші товари
        context['new_arrivals'] = Product.objects.order_by('-created_at')[:4]
        # 4 бестселери (для демонстрації візьмемо випадкові)
        context['bestsellers'] = Product.objects.order_by('?')[:4]
        return context


class ProductListView(ListView):
    """
    Display a paginated, filterable, searchable product catalogue.
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Build queryset from service layer based on GET params."""
        params = self.request.GET
        search_query = params.get('search', '').strip()

        # Selection logic (Search or Base)
        if search_query:
            queryset = search_products(search_query)
        else:
            queryset = get_base_queryset()

        # Filtering logic
        queryset = filter_products(
            queryset,
            category_slug=params.get('category'),
            brands=params.getlist('brand'),
            min_price=params.get('min_price'),
            max_price=params.get('max_price'),
            volume=params.get('volume'),
            gender=params.get('gender'),
            fragrance_group=params.get('fragrance_group'),
        )

        return self._apply_sorting(queryset, params.get('sort'))

    def _apply_sorting(self, queryset, sort_param):
        """Helper to handle sorting logic."""
        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
        }
        order_field = sort_map.get(sort_param, '-created_at')
        return queryset.order_by(order_field)

    def get_context_data(self, **kwargs):
        """Inject catalog data and active filters into template context."""
        context = super().get_context_data(**kwargs)
        
        # Filter data
        context['categories'] = Category.objects.all()
        context['available_brands'] = (
            Product.objects.values_list('brand', flat=True)
            .distinct()
            .exclude(brand='')
            .order_by('brand')
        )
        context['available_fragrance_groups'] = (
            Product.objects.values_list('fragrance_group', flat=True)
            .distinct()
            .exclude(fragrance_group='')
            .order_by('fragrance_group')
        )
        
        # Price stats from service
        stats = get_catalog_stats()
        context['min_db_price'] = stats['min_price']
        context['max_db_price'] = stats['max_price']

        # Active filters state
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'brands': self.request.GET.getlist('brand'),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'volume': self.request.GET.get('volume', ''),
            'gender': self.request.GET.get('gender', ''),
            'fragrance_group': self.request.GET.get('fragrance_group', ''),
        }
        
        context['cart_product_form'] = CartAddProductForm()
        return context


class ProductDetailView(DetailView):
    """Display full details for a single product."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return get_base_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_product_form'] = CartAddProductForm()
        return context


def search_api(request):
    """JSON API for live search suggestions."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    products = search_products(query, limit=10)

    results = [
        {
            'name': p.name,
            'brand': p.brand,
            'url': p.get_absolute_url(),
            'image': p.image.url if p.image else None
        } for p in products
    ]

    return JsonResponse({'results': results})
