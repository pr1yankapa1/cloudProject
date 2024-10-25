import pandas as pd
from django.core.management.base import BaseCommand
from store.models import Planter, Category

class Command(BaseCommand):
    help = 'Import planters from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)

            # Print the columns to check names
            print("Columns in the Excel file:", df.columns.tolist())

            # Iterate through the DataFrame and create planters
            for index, row in df.iterrows():
                name = row['planter_name']  # Adjusted to match Excel column name
                price = row['price (USD)']  # Adjusted to match Excel column name
                category_name = row['category']  # Adjusted to match Excel column name
                description = row.get('description', '')  # Adjusted to match Excel column name
                size = row.get('size (cm)', '')  # Adjusted to match Excel column name
                color = row.get('color', '')  # Adjusted to match Excel column name
                material = row.get('material', '')  # Adjusted to match Excel column name

                # Get or create category
                category, created = Category.objects.get_or_create(name=category_name)

                # Create planter
                Planter.objects.create(
                    name=name,
                    price=price,
                    category=category,
                    description=description,
                    size=size,
                    color=color,
                    material=material
                )

            self.stdout.write(self.style.SUCCESS('Planters imported successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing planters: {e}'))
