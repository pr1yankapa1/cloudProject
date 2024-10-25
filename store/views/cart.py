from django.shortcuts import render,redirect
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_object_or_404
from store.models.customer import Customer
from django.views import View
from store.models.product import Product
from store.models.planters import Planter
# views.py

class Cart(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        items = []
        total_price = 0

        for item_key, quantity in cart.items():
            item_type, item_id = item_key.split('_')
            item_id = int(item_id)
            if item_type == 'product':
                item = get_object_or_404(Product, id=item_id)
            elif item_type == 'planter':
                item = get_object_or_404(Planter, id=item_id)
            else:
                continue  # Skip unknown item types

            item.total_price = item.price * quantity
            item.quantity = quantity
            item.item_key = item_key
            items.append(item)
            total_price += item.total_price

        context = {
            'items': items,
            'total_price': total_price,
        }

        return render(request, 'cart.html', context)
from django.shortcuts import redirect

class RemoveFromCart(View):
    def post(self, request, item_key):
        cart = request.session.get('cart', {})
        if item_key in cart:
            del cart[item_key]  # Remove item from cart
            request.session['cart'] = cart  # Update the session cart
        return redirect('cart')  # Redirect to cart view
