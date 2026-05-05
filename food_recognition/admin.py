from django.contrib import admin
from .models import FoodAnalysis, FoodItem

@admin.register(FoodAnalysis)
class FoodAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at', 'safety_level', 'confidence_score')
    list_filter = ('safety_level', 'uploaded_at')
    search_fields = ('user__username',)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'protein', 'carbs', 'fat')
    search_fields = ('name',)
