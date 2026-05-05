from django.contrib import admin
from .models import UserHealthProfile, DailyTracking, SavedFood

@admin.register(UserHealthProfile)
class UserHealthProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'weight', 'activity_level')
    search_fields = ('user__username',)

@admin.register(DailyTracking)
class DailyTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'water_intake', 'exercise_minutes', 'mood')
    list_filter = ('date', 'mood')
    search_fields = ('user__username',)

@admin.register(SavedFood)
class SavedFoodAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'user', 'safety_level', 'saved_at')
    search_fields = ('user__username', 'food_name')
