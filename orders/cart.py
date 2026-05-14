from decimal import Decimal
from typing import Any, Dict, Iterator

from django.conf import settings
from django.http import HttpRequest

from products.models import Product


class Cart:
    """
    Клас кошика (Cart), що керує станом товарів за допомогою сесій Django.
    
    Кошик дозволяє додавати товари, змінювати їхню кількість, видаляти їх
    та отримувати загальну вартість. Дані кошика зберігаються в сесії у форматі JSON.
    """

    def __init__(self, request: HttpRequest) -> None:
        """
        Ініціалізує кошик покупця.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            # Зберегти порожній кошик у сесії
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Додає товар до кошика або оновлює його кількість.
        
        :param product: Екземпляр моделі Product.
        :param quantity: Кількість товару для додавання.
        :param override_quantity: Якщо True - замінює поточну кількість, якщо False - додає до поточної.
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
            
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def save(self) -> None:
        """
        Позначає сесію як "змінену", щоб переконатися, що вона буде збережена.
        """
        self.session.modified = True

    def remove(self, product: Product) -> None:
        """
        Видаляє товар з кошика.
        
        :param product: Екземпляр моделі Product, який потрібно видалити.
        """
        product_id = str(product.id)
        
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self) -> None:
        """
        Видаляє кошик із поточних даних сесії.
        """
        del self.session[settings.CART_SESSION_ID]
        self.cart = {}
        self.save()

    def get_total_price(self) -> Decimal:
        """
        Отримує загальну вартість усіх товарів у кошику.
        """
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Проходить по товарах у кошику та отримує відповідні об'єкти Product з бази даних.
        """
        product_ids = self.cart.keys()
        
        # Отримуємо об'єкти товарів і додаємо їх у кошик
        products = Product.objects.filter(id__in=product_ids)
        
        cart_copy = self.cart.copy()
        
        for product in products:
            cart_copy[str(product.id)]['product'] = product
            
        for item in cart_copy.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """
        Повертає загальну кількість товарів у кошику.
        """
        return sum(item['quantity'] for item in self.cart.values())
