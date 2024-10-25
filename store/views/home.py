from django.shortcuts import render , redirect , HttpResponseRedirect
from store.models.product import Product
from store.models.category import Category
from store.models.planters import Planter
from django.views import View

class HomePage(View):
    def get(self, request):
        return render(request, 'home.html')
# Create your views here.
class Index(View):

    def post(self, request):
        product_id = request.POST.get('product')
        planter_id = request.POST.get('planter')
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})

        # Determine if the item is a product or a planter
        if product_id:
            item_id = product_id
            item_type = 'product'
        elif planter_id:
            item_id = planter_id
            item_type = 'planter'
        else:
            # No item provided
            return redirect('homepage')

        # Use a combined key to prevent ID collisions
        item_key = f"{item_type}_{item_id}"

        quantity = cart.get(item_key, 0)
        if remove:
            if quantity <= 1:
                cart.pop(item_key, None)
            else:
                cart[item_key] = quantity - 1
        else:
            cart[item_key] = quantity + 1

        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('homepage')

    def get(self, request):
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')



    def get(self , request):
        # print()
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')

def store(request):
    # Get the session cart; if none exists, initialize an empty cart
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}

    # Initialize products and planters variables
    products = None
    planters = None

    # Fetch all categories
    categories = Category.get_all_categories()

    # Get category ID from GET request parameters
    categoryID = request.GET.get('category')

    # Filter products and planters based on selected category, or get all if no category is selected
    if categoryID:
        products = Product.get_all_products_by_categoryid(categoryID)
        planters = Planter.get_all_planters_by_categoryid(categoryID)
    else:
        products = Product.get_all_products()
        planters = Planter.get_all_planters()

    # Data to pass to the template
    data = {
        'products': products,
        'planters': planters,
        'categories': categories,
    }

    # Print the current user's email stored in the session (for debugging)
    print('you are : ', request.session.get('email'))

    # Render the template with the data
    return render(request, 'index.html', data)

from django.shortcuts import render, get_object_or_404, redirect
from store.models.product import Product
from store.models.category import Category
from django.views import View

# views.py

# Existing imports...
from store.models.planters import Planter

# Product Detail View
class ProductDetail(View):

    def get(self, request, product_id):
        # Get the specific product
        product = get_object_or_404(Product, id=product_id)

        # Fetch recommended products based on category
        recommendations = Product.get_all_products_by_categoryid(product.category.id).exclude(id=product_id)[:4]
        planter_recommendations = Planter.objects.all()[:4]
        context = {
            'product': product,
            'recommendations': recommendations,
            'planter_recommendations': planter_recommendations,  # Make sure this is passed
            'categories': Category.objects.all(),
        }

        return render(request, 'product_detail.html', context)

    def post(self, request, product_id):
        # Similar to previous code, adjusted for item_key
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        item_key = f"product_{product_id}"

        if quantity < 1:
            quantity = 1

        cart[item_key] = cart.get(item_key, 0) + quantity
        request.session['cart'] = cart

        return redirect('product_detail', product_id=product.id)
# views.py
class PlanterDetail(View):

    def get(self, request, planter_id):
        # Get the specific planter
        planter = get_object_or_404(Planter, id=planter_id)

        # Fetch recommended planters (exclude the current planter and fetch 3 from the same category)
        recommendations = Planter.objects.filter(category=planter.category).exclude(id=planter.id)[:3]

        # Fetch recommended products (this could be refined based on your logic)
        product_recommendations = Product.objects.all()[:4]  # Adjust as necessary to fit your recommendation logic

        # Fetch all categories for the sidebar
        categories = Category.objects.all()

        context = {
            'planter': planter,
            'recommendations': recommendations,
            'product_recommendations': product_recommendations,
            'categories': categories,
        }

        return render(request, 'planter_detail.html', context)

    def post(self, request, planter_id):
        # Handle adding the planter to the cart
        planter = get_object_or_404(Planter, id=planter_id)
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        item_key = f"planter_{planter_id}"

        if quantity < 1:
            quantity = 1

        cart[item_key] = cart.get(item_key, 0) + quantity
        request.session['cart'] = cart

        return redirect('planter_detail', planter_id=planter.id)

from django.core.mail import send_mail
from django.conf import settings

class ContactView(View):
    def post(self, request):
        email = request.POST.get('email')
        message = request.POST.get('message')
        if email and message:
            # Send email (optional)
            send_mail(
                'New Contact Us Message',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Send to store email
                fail_silently=False,
            )
            return redirect('home')
        return redirect('home')
