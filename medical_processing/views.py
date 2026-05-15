from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MedicalReport, ExtractedHealthInfo, Allergy, DietaryRestriction
from .serializers import MedicalReportSerializer, MedicalReportListSerializer
from .nlp_service import MedicalDocumentProcessor
from recommendations.models import Recommendation

class MedicalReportViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalReportSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return MedicalReport.objects.filter(user=self.request.user)
        return MedicalReport.objects.filter(user=None)

    def destroy(self, request, *args, **kwargs):
        """Delete medical report and associated recommendations"""
        report = self.get_object()
        user = request.user if request.user.is_authenticated else None

        # Delete all recommendations for this user
        # (since they were generated based on this report)
        Recommendation.objects.filter(user=user).delete()

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        if 'document' not in request.FILES:
            return Response({'error': 'No document provided'}, status=status.HTTP_400_BAD_REQUEST)

        document = request.FILES['document']

        medical_report = MedicalReport.objects.create(
            user=request.user if request.user.is_authenticated else None,
            document=document,
            status='processing'
        )

        try:
            result = MedicalDocumentProcessor.process_medical_document(document)

            # Clean up temp files to save storage
            try:
                import os
                import tempfile
                temp_dir = tempfile.gettempdir()
                # Delete old temp files (older than 1 hour)
                import time
                current_time = time.time()
                for filename in os.listdir(temp_dir):
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.isfile(filepath) and (current_time - os.path.getmtime(filepath)) > 3600:
                        try:
                            os.remove(filepath)
                        except:
                            pass
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Temp file cleanup failed: {cleanup_error}")

            for condition in result['conditions']:
                ExtractedHealthInfo.objects.create(
                    report=medical_report,
                    condition_name=condition['condition'],
                    confidence=condition['confidence'],
                    description=f"Detected from medical document",
                    severity=condition['severity']
                )

            for allergen in result['allergens']:
                Allergy.objects.create(
                    report=medical_report,
                    allergen=allergen['allergen'],
                    reaction_type='unknown',
                    severity=allergen['severity'],
                    confidence=allergen['confidence']
                )

            for restriction in result['dietary_restrictions']:
                DietaryRestriction.objects.create(
                    report=medical_report,
                    restriction=restriction['restriction'],
                    reason=restriction['reason'],
                    recommendation=restriction['recommendation']
                )

            medical_report.extracted_data = {
                'conditions': result['conditions'],
                'allergens': result['allergens'],
                'dietary_restrictions': result['dietary_restrictions'],
                'is_mock': result.get('is_mock', False),
                'extraction_method': result.get('extraction_method', 'unknown'),
                'extracted_summary': result.get('extracted_summary'),  # AI summary if available
                'raw_text_preview': result['raw_text'][:500] if result['raw_text'] else ''
            }
            medical_report.raw_text = result['raw_text']
            medical_report.status = 'completed'
            medical_report.save()

            serializer = MedicalReportSerializer(medical_report, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            medical_report.status = 'error'
            medical_report.processing_error = str(e)
            medical_report.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        limit = request.query_params.get('limit', 10)
        recent_reports = self.get_queryset()[:int(limit)]
        serializer = MedicalReportListSerializer(recent_reports, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def health_summary(self, request):
        reports = self.get_queryset().filter(status='completed')

        all_conditions = []
        all_allergens = []
        all_restrictions = []

        for report in reports:
            health_info = report.health_info.all()
            all_conditions.extend([
                {
                    'condition': hi.condition_name,
                    'severity': hi.severity,
                    'confidence': hi.confidence
                }
                for hi in health_info
            ])

            allergies = report.allergies.all()
            all_allergens.extend([
                {
                    'allergen': a.allergen,
                    'severity': a.severity,
                    'confidence': a.confidence
                }
                for a in allergies
            ])

            restrictions = report.dietary_restrictions.all()
            all_restrictions.extend([
                {
                    'restriction': r.restriction,
                    'reason': r.reason,
                    'recommendation': r.recommendation
                }
                for r in restrictions
            ])

        return Response({
            'conditions': all_conditions,
            'allergens': all_allergens,
            'dietary_restrictions': all_restrictions,
            'report_count': reports.count()
        })
