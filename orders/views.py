from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm
from .models import OrderItem


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponseRedirect:
    """
    Додає товар до кошика або оновлює його кількість на основі даних з форми.

    :param request: Об'єкт HttpRequest.
    :param product_id: Ідентифікатор товару (Product).
    :return: HttpResponseRedirect: Перенаправлення на сторінку детального перегляду кошика.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    
    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponseRedirect:
    """
    Видаляє вказаний товар із поточного кошика сесії.

    :param request: Об'єкт HttpRequest.
    :param product_id: Ідентифікатор товару (Product).
    :return: HttpResponseRedirect: Перенаправлення на сторінку детального перегляду кошика.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    return redirect('orders:cart_detail')


def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Відображає вміст кошика та генерує форми для оновлення кількості
    кожного товару безпосередньо на сторінці кошика.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse: Відрендерений шаблон 'orders/cart_detail.html' з контекстом.
    """
    cart = Cart(request)
    
    # Для кожного товару в кошику створюємо форму, щоб можна було змінити його кількість
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={
                'quantity': item['quantity'],
                'override': True
            }
        )
        
    return render(request, 'orders/cart_detail.html', {'cart': cart})


def order_create(request: HttpRequest) -> HttpResponse:
    """
    Обробляє оформлення замовлення:
    - Якщо GET: відображає пусту форму.
    - Якщо POST: валідує дані, створює замовлення, переносить
      товари з кошика в OrderItem та очищує кошик.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse: Відрендерений шаблон.
    """
    cart = Cart(request)
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
                
            # Очищуємо кошик після успішного збереження товарів
            cart.clear()
            return render(request, 'orders/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()
        
    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})
