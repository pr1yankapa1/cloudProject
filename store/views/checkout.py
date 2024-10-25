import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from store.models.product import Product
from store.models.planters import Planter
from store.models.orders import Order
from store.models.customer import Customer
import paypalrestsdk
from django.conf import settings

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')
        customer_id = request.session.get('customer')
        cart = request.session.get('cart', {})
        
        items = []
        total_price = 0

        # Fetch both products and planters from the cart
        for item_key, quantity in cart.items():
            parts = item_key.split('_')
            if len(parts) != 2:
                continue  # Skip malformed keys
            
            item_type, item_id = parts
            item_id = int(item_id)

            if item_type == 'product':
                item = get_object_or_404(Product, id=item_id)
            elif item_type == 'planter':
                item = get_object_or_404(Planter, id=item_id)
            else:
                continue  # Skip unknown item types

            item.total_price = item.price * quantity
            item.quantity = quantity
            items.append(item)
            total_price += item.total_price

        # Handle PayPal Online Payment
        if payment_method == "online":
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": request.build_absolute_uri('/payment-success'),
                    "cancel_url": request.build_absolute_uri('/payment-cancel')
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": item.name,
                            "sku": item.id,
                            "price": str(item.price),
                            "currency": "USD",
                            "quantity": item.quantity
                        } for item in items]
                    },
                    "amount": {
                        "total": str(total_price),
                        "currency": "USD"
                    },
                    "description": "Payment for order"
                }]
            })

            if payment.create():
                approval_url = next((str(link.href) for link in payment.links if link.rel == "approval_url"), None)
                if approval_url:
                    # Store order details in session before redirecting to PayPal
                    request.session['order_address'] = address
                    request.session['order_phone'] = phone
                    request.session['payment_method'] = payment_method
                    return redirect(approval_url)
            else:
                logging.error(f"PayPal payment creation failed: {payment.error}")
                return JsonResponse({"error": payment.error}, status=400)

        # Handle Cash on Delivery (COD)
        for item in items:
            order = Order(
                customer=Customer(id=customer_id),
                product=item if isinstance(item, Product) else None,
                planter=item if isinstance(item, Planter) else None,  # Use this field if Planter is part of the Order model
                price=item.price,
                address=address,
                phone=phone,
                quantity=item.quantity,
                payment_method=payment_method
            )
            order.place_order()

        # Clear the cart after creating the orders
        request.session['cart'] = {}
        return redirect('cart')

def payment_success(request):
    # Retrieve address, phone, and payment method from the session
    address = request.session.get('order_address')
    phone = request.session.get('order_phone')
    payment_method = request.session.get('payment_method', 'online')  # Default to "online"

    # Get the cart data
    cart = request.session.get('cart', {})
    items = []  # To store both products and planters
    total_amount = 0

    # Process the cart items (Product or Planter)
    for item_key, quantity in cart.items():
        # Each cart item key is expected to be like 'product_8' or 'planter_3'
        item_type, item_id_str = item_key.split('_')  # Split to get type and ID as strings
        item_id = int(item_id_str)  # Convert the item ID to an integer

        if item_type == 'product':
            # If the item is a product, fetch from the Product model
            product = get_object_or_404(Product, id=item_id)
            product.quantity = quantity
            product.total_price = product.price * quantity
            items.append(product)
            total_amount += product.total_price
        elif item_type == 'planter':
            # If the item is a planter, fetch from the Planter model
            planter = get_object_or_404(Planter, id=item_id)
            planter.quantity = quantity
            planter.total_price = planter.price * quantity
            items.append(planter)
            total_amount += planter.total_price

    # Place orders after confirming successful payment
    customer_id = request.session.get('customer')
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        for item in items:
            if isinstance(item, Product):
                order = Order(
                    customer=customer,
                    product=item,  # Set product if it's a product
                    planter=None,  # Set planter to None
                    price=item.price,
                    address=address,
                    phone=phone,
                    quantity=item.quantity,
                    payment_method=payment_method,
                    paid=(payment_method == 'online')  # Set paid to True if payment method is online
                )
            elif isinstance(item, Planter):
                order = Order(
                    customer=customer,
                    product=None,  # Set product to None
                    planter=item,  # Set planter if it's a planter
                    price=item.price,
                    address=address,
                    phone=phone,
                    quantity=item.quantity,
                    payment_method=payment_method,
                    paid=(payment_method == 'online')  # Set paid to True if payment method is online
                )
            order.place_order()

    # Clear the cart and session data after placing orders
    request.session['cart'] = {}
    request.session['order_address'] = None
    request.session['order_phone'] = None
    request.session['payment_method'] = None

    context = {
        'message': 'Payment was successful!',
        'items': items,  # List of products and planters
        'cart': {},  # Clear the cart in the template
        'total_amount': total_amount,
    }
    return render(request, 'payment_success.html', context)
