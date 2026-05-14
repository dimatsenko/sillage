"""
Models for the Products & Catalog module.

Defines Category and Product entities for the Sillage perfume decant store.
"""
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """
    Product category (e.g. "Нішева парфумерія", "Арабська парфумерія").

    Fields:
        name  — human-readable category title (unique, indexed).
        slug  — URL-safe identifier used in filtering and future SEO URLs.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name='Назва',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name='Слаг (URL)',
        help_text='Унікальний ідентифікатор для URL (тільки латиниця, цифри, дефіси)',
    )

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """
    A perfume decant product available in the store.

    Fields:
        name            — product display name.
        brand           — perfume house / brand.
        description     — rich-text product description.
        price           — price in UAH (≥ 0.01).
        volume          — decant volume in ml (≥ 1).
        category        — FK to Category.
        gender          — gender category.
        fragrance_group — fragrance group (e.g. Floral, Woody).
        created_at      — auto-set on creation.
        updated_at      — auto-set on every save.
    """

    class Gender(models.TextChoices):
        MALE = 'M', 'Чоловічі'
        FEMALE = 'F', 'Жіночі'
        UNISEX = 'U', 'Унісекс'

    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='Назва',
    )
    brand = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='Бренд',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Опис',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Ціна (грн)',
    )
    volume = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Об'єм (мл)",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Категорія',
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        default=Gender.UNISEX,
        verbose_name='Стать',
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Фотографія',
    )
    fragrance_group = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Група ароматів',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата оновлення',
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'name'], name='idx_product_brand_name'),
            models.Index(fields=['price'], name='idx_product_price'),
            models.Index(fields=['-created_at'], name='idx_product_created'),
        ]

    def __str__(self) -> str:
        return f'{self.brand} — {self.name} ({self.volume} мл)'

    def get_absolute_url(self) -> str:
        """Return canonical URL for the product detail page."""
        return reverse('products:detail', kwargs={'pk': self.pk})
