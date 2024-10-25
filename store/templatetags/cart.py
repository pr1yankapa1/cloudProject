# templatetags/cart.py

from django import template

register = template.Library()

@register.filter(name='is_in_cart')
def is_in_cart(item_key, cart):
    return item_key in cart

@register.filter(name='cart_quantity')
def cart_quantity(item_key, cart):
    return cart.get(item_key, 0)

@register.filter(name='price_total')
def price_total(item, cart):
    item_key = f"{item.__class__.__name__.lower()}_{item.id}"
    return item.price * cart_quantity(item_key, cart)

@register.filter(name='total_cart_price')
def total_cart_price(items, cart):
    total_sum = 0
    for item in items:
        item_key = f"{item.__class__.__name__.lower()}_{item.id}"
        total_sum += price_total(item, cart)
    return total_sum
