from rest_framework import serializers
from .models import Recommendation, RecommendationHistory

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'food_item', 'description', 'condition', 'benefit', 'severity', 'nutritional_info', 'created_at']

class RecommendationHistorySerializer(serializers.ModelSerializer):
    recommendation = RecommendationSerializer(read_only=True)

    class Meta:
        model = RecommendationHistory
        fields = ['id', 'recommendation', 'viewed_at', 'action']
