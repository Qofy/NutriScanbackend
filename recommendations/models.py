from django.db import models
from django.contrib.auth.models import User

class Recommendation(models.Model):
    SEVERITY_CHOICES = [
        ('safe', 'Safe'),
        ('caution', 'Caution'),
        ('danger', 'Danger'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.CharField(max_length=255)
    description = models.TextField()
    condition = models.CharField(max_length=255)
    benefit = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    nutritional_info = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    based_on_food_analysis = models.BooleanField(default=False)
    based_on_medical_report = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.food_item} for {self.user.username}"


class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, choices=[
        ('viewed', 'Viewed'),
        ('saved', 'Saved'),
        ('dismissed', 'Dismissed'),
        ('followed', 'Followed'),
    ])

    class Meta:
        ordering = ['-viewed_at']
