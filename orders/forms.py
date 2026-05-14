from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order

# Вибір кількості від 1 до 20
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    """
    Форма для додавання товару в кошик та оновлення його кількості.
    """
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        label=_("Кількість"),
        help_text=_("Оберіть кількість товару для додавання.")
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )


class OrderCreateForm(forms.ModelForm):
    """
    Форма оформлення замовлення, яка збирає дані про покупця
    та зберігає їх у моделі Order.
    """
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'city']
