"""URL routing for the Products & Catalog module."""
from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('api/search/', views.search_api, name='search_api'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='detail'),
]
