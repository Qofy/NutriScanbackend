from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import FoodAnalysis, FoodItem
from .yolo_service import yolo_detector
from .nutrition_service import evaluate_safety, get_nutritional_info

class FoodAnalysisTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_food_item(self):
        food = FoodItem.objects.create(
            name='Test Apple',
            calories=95,
            protein=0.5,
            carbs=25,
            fat=0.3,
            fiber=4.4
        )
        self.assertEqual(food.name, 'Test Apple')
        self.assertEqual(food.calories, 95)

    def test_food_safety_evaluation(self):
        health_profile = {
            'conditions': ['diabetes'],
            'allergens': []
        }
        food_items = [{'name': 'Apple', 'confidence': 0.95}]
        safety_level, reason = evaluate_safety(food_items, health_profile)
        self.assertEqual(safety_level, 'safe')

    def test_nutritional_info_lookup(self):
        food_items = [{'name': 'Apple', 'confidence': 0.95}]
        nutrition = get_nutritional_info(food_items)
        self.assertIn('apple', nutrition)
