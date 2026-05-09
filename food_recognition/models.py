from django.db import models
from django.contrib.auth.models import User

class FoodAnalysis(models.Model):
    SAFETY_CHOICES = [
        ('safe', 'Safe'),
        ('caution', 'Caution'),
        ('danger', 'Danger'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(upload_to='food_analysis/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis_result = models.JSONField(default=dict)
    recognized_items = models.JSONField(default=list)
    nutritional_info = models.JSONField(default=dict)
    safety_level = models.CharField(max_length=10, choices=SAFETY_CHOICES, default='safe')
    confidence_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Food Analysis - {self.user.username} - {self.uploaded_at}"


class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    fiber = models.FloatField()
    vitamins = models.JSONField(default=dict)
    minerals = models.JSONField(default=dict)
    allergens = models.JSONField(default=list)

    def __str__(self):
        return self.name
