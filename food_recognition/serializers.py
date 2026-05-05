from rest_framework import serializers
from .models import FoodAnalysis, FoodItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'

class FoodAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAnalysis
        fields = ['id', 'image', 'uploaded_at', 'recognized_items', 'nutritional_info', 'safety_level', 'confidence_score', 'analysis_result']
        read_only_fields = ['analysis_result', 'recognized_items', 'nutritional_info', 'safety_level', 'confidence_score']

class FoodAnalysisListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAnalysis
        fields = ['id', 'uploaded_at', 'recognized_items', 'safety_level']
