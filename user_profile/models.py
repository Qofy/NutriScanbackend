from django.db import models
from django.contrib.auth.models import User

class UserHealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    country = models.CharField(max_length=100, blank=True, null=True, help_text="User's country for regional food recommendations")
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    activity_level = models.CharField(max_length=50, choices=[
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extremely_active', 'Extremely Active'),
    ], default='moderately_active')
    dietary_preferences = models.JSONField(default=list)
    allergies = models.JSONField(default=list)
    health_conditions = models.JSONField(default=list)
    dietary_restrictions = models.JSONField(default=list)
    medications = models.JSONField(default=list)
    goals = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health Profile - {self.user.username}"

    def get_bmi(self):
        if self.height and self.weight:
            return round(self.weight / ((self.height / 100) ** 2), 2)
        return None


class DailyTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    meals = models.JSONField(default=list)
    water_intake = models.FloatField(default=0, help_text="in liters")
    exercise_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    mood = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('neutral', 'Neutral'),
        ('poor', 'Poor'),
    ], blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Daily Tracking - {self.user.username} - {self.date}"


class SavedFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=255)
    nutritional_info = models.JSONField()
    safety_level = models.CharField(max_length=10)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.food_name} - {self.user.username}"
