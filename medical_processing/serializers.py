from rest_framework import serializers
from .models import MedicalReport, ExtractedHealthInfo, Allergy, DietaryRestriction

class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ['allergen', 'reaction_type', 'severity', 'confidence']

class ExtractedHealthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedHealthInfo
        fields = ['condition_name', 'confidence', 'description', 'severity']

class DietaryRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryRestriction
        fields = ['restriction', 'reason', 'recommendation']

class MedicalReportSerializer(serializers.ModelSerializer):
    health_info = ExtractedHealthInfoSerializer(many=True, read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)
    dietary_restrictions = DietaryRestrictionSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalReport
        fields = ['id', 'document', 'uploaded_at', 'status', 'extracted_data', 'health_info', 'allergies', 'dietary_restrictions']
        read_only_fields = ['extracted_data', 'status']

class MedicalReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalReport
        fields = ['id', 'uploaded_at', 'status']
