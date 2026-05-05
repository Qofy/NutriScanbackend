from django.core.management.base import BaseCommand
from food_recognition.models import FoodItem

class Command(BaseCommand):
    help = 'Seed database with initial food items'

    def handle(self, *args, **options):
        foods_data = [
            {
                'name': 'Apple',
                'calories': 95,
                'protein': 0.5,
                'carbs': 25,
                'fat': 0.3,
                'fiber': 4.4,
                'vitamins': {'C': '8.4mg', 'A': '54IU'},
                'minerals': {'potassium': '195mg'},
                'allergens': []
            },
            {
                'name': 'Carrot',
                'calories': 41,
                'protein': 0.9,
                'carbs': 10,
                'fat': 0.2,
                'fiber': 2.8,
                'vitamins': {'A': '961mcg', 'C': '3.6mg'},
                'minerals': {'potassium': '320mg'},
                'allergens': []
            },
            {
                'name': 'Spinach',
                'calories': 23,
                'protein': 2.7,
                'carbs': 3.6,
                'fat': 0.4,
                'fiber': 2.2,
                'vitamins': {'K': '145mcg', 'A': '4623IU'},
                'minerals': {'iron': '0.8mg'},
                'allergens': []
            },
            {
                'name': 'Salmon',
                'calories': 208,
                'protein': 20,
                'carbs': 0,
                'fat': 13,
                'fiber': 0,
                'vitamins': {'B12': '3.2mcg', 'D': '600IU'},
                'minerals': {'selenium': '44mcg'},
                'allergens': ['fish']
            },
            {
                'name': 'Peanuts',
                'calories': 567,
                'protein': 25.8,
                'carbs': 16.1,
                'fat': 49.2,
                'fiber': 8.6,
                'vitamins': {'E': '8.3mg'},
                'minerals': {'magnesium': '168mg'},
                'allergens': ['peanuts']
            },
        ]

        for food_data in foods_data:
            food, created = FoodItem.objects.get_or_create(
                name=food_data['name'],
                defaults=food_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created food: {food.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Food already exists: {food.name}'))

        self.stdout.write(self.style.SUCCESS('Food seeding completed'))
