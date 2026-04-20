from django.http import HttpRequest
from .cart import Cart

def cart(request: HttpRequest) -> dict:
    """
    Context processor, що забезпечує доступ до об'єкта кошика
    з усіх HTML-шаблонів сайту.
    """
    return {'cart': Cart(request)}
