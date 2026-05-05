from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserHealthProfile, DailyTracking, SavedFood

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserHealthProfileSerializer(serializers.ModelSerializer):
    bmi = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserHealthProfile
        fields = ['id', 'user', 'age', 'gender', 'height', 'weight', 'bmi', 'activity_level',
                  'dietary_preferences', 'allergies', 'health_conditions', 'dietary_restrictions',
                  'medications', 'goals', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_bmi(self, obj):
        return obj.get_bmi()

class DailyTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTracking
        fields = ['id', 'user', 'date', 'meals', 'water_intake', 'exercise_minutes', 'notes', 'mood']
        read_only_fields = ['id', 'date']

class SavedFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedFood
        fields = ['id', 'food_name', 'nutritional_info', 'safety_level', 'saved_at']
        read_only_fields = ['id', 'saved_at']
