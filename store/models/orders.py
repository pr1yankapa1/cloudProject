from django.db import models
from .product import Product
from .customer import Customer
from .planters import Planter
from django.utils import timezone

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)  # Nullable Product
    planter = models.ForeignKey(Planter, on_delete=models.CASCADE, null=True, blank=True)  # Nullable Planter
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255, default='', blank=True)
    phone = models.CharField(max_length=50, default='', blank=True)
    date = models.DateField(default=timezone.now)
    status = models.BooleanField(default=False)  # Indicates if order is completed
    paid = models.BooleanField(default=False)  # New field to track payment status
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def place_order(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')
    def __str__(self):
            if self.product:
                return f"Order for Product: {self.product.name} (x{self.quantity})"
            elif self.planter:
                return f"Order for Planter: {self.planter.name} (x{self.quantity})"
            return f"Order ID: {self.id}"