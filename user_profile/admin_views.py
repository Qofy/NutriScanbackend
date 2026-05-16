from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db.models import Count, Q
from food_recognition.models import FoodAnalysis
from medical_processing.models import MedicalReport
from user_profile.models import UserHealthProfile
from user_profile.serializers import UserSerializer
from user_profile.permissions import IsAdminRole


class AdminViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def list(self, request):
        return Response({'message': 'Admin API'})

    @action(detail=False, methods=['GET'], url_path='stats')
    def stats(self, request):
        total_users = User.objects.count()
        total_scans = FoodAnalysis.objects.count()
        total_reports = MedicalReport.objects.count()

        safety_breakdown = FoodAnalysis.objects.values('safety_level').annotate(count=Count('id'))
        safety_dict = {item['safety_level']: item['count'] for item in safety_breakdown}

        manual_count = FoodAnalysis.objects.filter(is_manual=True).count()
        auto_count = total_scans - manual_count

        recent_scans = FoodAnalysis.objects.select_related('user').order_by('-uploaded_at')[:5].values(
            'id', 'user__username', 'recognized_items', 'safety_level', 'uploaded_at'
        )

        recent_reports = MedicalReport.objects.select_related('user').order_by('-uploaded_at')[:5].values(
            'id', 'user__username', 'status', 'uploaded_at'
        )

        return Response({
            'total_users': total_users,
            'total_scans': total_scans,
            'total_reports': total_reports,
            'safety_breakdown': {
                'safe': safety_dict.get('safe', 0),
                'caution': safety_dict.get('caution', 0),
                'danger': safety_dict.get('danger', 0),
            },
            'scan_type_breakdown': {
                'manual': manual_count,
                'auto': auto_count,
            },
            'recent_scans': list(recent_scans),
            'recent_reports': list(recent_reports),
        })

    @action(detail=False, methods=['GET'], url_path='users')
    def list_users(self, request):
        users = User.objects.annotate(
            scan_count=Count('foodanalysis', distinct=True),
            report_count=Count('medicalreport', distinct=True)
        ).values('id', 'username', 'email', 'date_joined', 'scan_count', 'report_count')

        result = []
        for user in users:
            try:
                role = UserHealthProfile.objects.get(user_id=user['id']).role
            except UserHealthProfile.DoesNotExist:
                role = 'user'

            result.append({**user, 'role': role})

        return Response(result)

    @action(detail=False, methods=['PUT'], url_path='users/(?P<pk>[^/.]+)/role')
    def update_role(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            profile, _ = UserHealthProfile.objects.get_or_create(user=user)
            new_role = request.data.get('role', 'user')

            if new_role not in ['user', 'admin']:
                return Response({'error': 'Invalid role'}, status=400)

            profile.role = new_role
            profile.save()

            return Response({'success': True, 'role': new_role})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

    @action(detail=False, methods=['GET'], url_path='scans')
    def list_scans(self, request):
        scans = FoodAnalysis.objects.select_related('user').all()

        safety_filter = request.query_params.get('safety')
        if safety_filter:
            scans = scans.filter(safety_level=safety_filter)

        manual_filter = request.query_params.get('manual')
        if manual_filter == 'true':
            scans = scans.filter(is_manual=True)
        elif manual_filter == 'false':
            scans = scans.filter(is_manual=False)

        scans = scans.order_by('-uploaded_at')[:100].values(
            'id', 'user__username', 'recognized_items', 'safety_level', 'is_manual', 'confidence_score', 'uploaded_at'
        )

        return Response(list(scans))

    @action(detail=False, methods=['GET'], url_path='reports')
    def list_reports(self, request):
        reports = MedicalReport.objects.select_related('user').all()

        status_filter = request.query_params.get('status')
        if status_filter:
            reports = reports.filter(status=status_filter)

        reports = reports.order_by('-uploaded_at')[:100].values(
            'id', 'user__username', 'status', 'uploaded_at', 'extracted_data'
        )

        result = []
        for report in reports:
            conditions_count = 0
            if report.get('extracted_data') and isinstance(report.get('extracted_data'), dict):
                extracted = report['extracted_data']
                if 'health_conditions' in extracted and isinstance(extracted['health_conditions'], list):
                    conditions_count = len(extracted['health_conditions'])

            result.append({**report, 'conditions_count': conditions_count})

        return Response(result)
