from rest_framework import serializers
from .models import FoodAnalysis, FoodItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'

class FoodAnalysisSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = FoodAnalysis
        fields = ['id', 'image', 'uploaded_at', 'recognized_items', 'nutritional_info', 'safety_level', 'confidence_score', 'analysis_result', 'is_manual']
        read_only_fields = ['analysis_result', 'recognized_items', 'nutritional_info', 'safety_level', 'confidence_score', 'is_manual']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image.url
            if request:
                return request.build_absolute_uri(image_url)
            return f'http://localhost:8000{image_url}'
        return None

class FoodAnalysisListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = FoodAnalysis
        fields = ['id', 'image', 'uploaded_at', 'recognized_items', 'safety_level', 'is_manual']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image.url
            if request:
                return request.build_absolute_uri(image_url)
            return f'http://localhost:8000{image_url}'
        return None
