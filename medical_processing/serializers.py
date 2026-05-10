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
    document = serializers.SerializerMethodField()
    health_info = ExtractedHealthInfoSerializer(many=True, read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)
    dietary_restrictions = DietaryRestrictionSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalReport
        fields = ['id', 'document', 'uploaded_at', 'status', 'extracted_data', 'health_info', 'allergies', 'dietary_restrictions']
        read_only_fields = ['extracted_data', 'status']

    def get_document(self, obj):
        request = self.context.get('request')
        if obj.document:
            doc_url = obj.document.url
            if request:
                return request.build_absolute_uri(doc_url)
            return f'http://localhost:8000{doc_url}'
        return None

class MedicalReportListSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()

    class Meta:
        model = MedicalReport
        fields = ['id', 'document', 'uploaded_at', 'status']

    def get_document(self, obj):
        request = self.context.get('request')
        if obj.document:
            doc_url = obj.document.url
            if request:
                return request.build_absolute_uri(doc_url)
            return f'http://localhost:8000{doc_url}'
        return None
