"""
Views for the Products & Catalog module.

Uses class-based views for consistency and extensibility.
All heavy logic is delegated to ``services.py``.
"""
from django.db.models import Max, Min, Q
from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from .models import Category, Product
from .services import filter_products, get_base_queryset, search_products
from orders.forms import CartAddProductForm


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

        # Sorting logic
        sort = params.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        """Inject categories and active filters into template context."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # Fetch distinct brands and fragrance groups that actually exist in the DB for the filter list
        context['available_brands'] = Product.objects.values_list('brand', flat=True).distinct().exclude(brand='').order_by('brand')
        context['available_fragrance_groups'] = Product.objects.values_list('fragrance_group', flat=True).distinct().exclude(fragrance_group='').order_by('fragrance_group')
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
        # Calculate price bounds for the filter
        price_stats = Product.objects.aggregate(min_p=Min('price'), max_p=Max('price'))
        context['min_db_price'] = int(price_stats['min_p'] or 0)
        context['max_db_price'] = int(price_stats['max_p'] or 0)
        
        context['cart_product_form'] = CartAddProductForm()
        return context


class ProductDetailView(DetailView):
    """Display full details for a single product."""

    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Use select_related to avoid extra queries on the detail page."""
        return get_base_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_product_form'] = CartAddProductForm()
        return context


from django.db.models import Q

def search_api(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(
        Q(name__icontains=query) | Q(brand__icontains=query)
    )[:10]

    results = []
    for p in products:
        results.append({
            'name': p.name,
            'brand': p.brand,
            'url': p.get_absolute_url(),
            'image': p.image.url if p.image else None
        })

    return JsonResponse({'results': results})
