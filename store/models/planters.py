from django.db import models
from .category import Category

class Planter(models.Model):
    name = models.CharField(max_length=100)  # Name of the planter
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the planter
    description = models.TextField()  # Description of the planter
    size = models.CharField(max_length=20)  # Size of the planter (e.g., 30cm)
    color = models.CharField(max_length=30)  # Color of the planter
    material = models.CharField(max_length=50)  # Material of the planter (e.g., ceramic, plastic)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Link to the Category model
    image = models.ImageField(upload_to='products/', blank=True, null=True, default='path/to/default/image.jpg')  # Image field with default image
    
    @staticmethod
    def get_all_planters():
        return Planter.objects.all()
    
     # Static method to fetch planters by category ID
    @staticmethod
    def get_all_planters_by_categoryid(category_id):
        return Planter.objects.filter(category=category_id)
    def __str__(self):
            return self.name
