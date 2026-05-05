from django.contrib import admin
from .models import Recommendation, RecommendationHistory

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('food_item', 'user', 'severity', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('user__username', 'food_item')

@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation', 'action', 'viewed_at')
    list_filter = ('action', 'viewed_at')
    search_fields = ('user__username',)
