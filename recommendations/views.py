from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Recommendation, RecommendationHistory
from .serializers import RecommendationSerializer, RecommendationHistorySerializer
from .engine import RecommendationEngine
from medical_processing.models import MedicalReport

class RecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Recommendation.objects.filter(user=self.request.user)
        return Recommendation.objects.none()

    @action(detail=False, methods=['post'])
    def generate(self, request):
        user_profile = request.data.get('profile', {})

        recommendations = RecommendationEngine.generate_recommendations(user_profile)

        created_recommendations = []
        for rec in recommendations:
            recommendation_obj = Recommendation.objects.create(
                user=request.user,
                food_item=rec['food_item'],
                description=rec['description'],
                condition=rec['condition'],
                benefit=rec['benefit'],
                severity=rec['severity'],
                nutritional_info=rec.get('nutrition', {})
            )
            created_recommendations.append(recommendation_obj)

        serializer = RecommendationSerializer(created_recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def personalized(self, request):
        conditions = request.query_params.getlist('conditions', [])
        allergens = request.query_params.getlist('allergens', [])

        user_profile = {
            'conditions': conditions,
            'allergens': allergens
        }

        recommendations = RecommendationEngine.generate_recommendations(user_profile)

        return Response({
            'recommendations': recommendations,
            'count': len(recommendations),
            'profile': user_profile
        })

    @action(detail=False, methods=['get'])
    def tips(self, request):
        conditions = request.query_params.getlist('conditions', [])
        allergens = request.query_params.getlist('allergens', [])

        user_profile = {
            'conditions': conditions,
            'allergens': allergens
        }

        tips = RecommendationEngine.get_personalized_tips(user_profile)

        return Response({
            'tips': tips,
            'profile': user_profile
        })

    @action(detail=False, methods=['get'])
    def health_based(self, request):
        try:
            reports = MedicalReport.objects.filter(user=request.user, status='completed')

            conditions = []
            allergens = []

            for report in reports:
                for health_info in report.health_info.all():
                    conditions.append(health_info.condition_name)

                for allergy in report.allergies.all():
                    allergens.append(allergy.allergen)

            user_profile = {
                'conditions': list(set(conditions)),
                'allergens': list(set(allergens))
            }

            recommendations = RecommendationEngine.generate_recommendations(user_profile)

            return Response({
                'recommendations': recommendations,
                'count': len(recommendations),
                'source': 'medical_reports',
                'profile': user_profile
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def track_action(self, request):
        recommendation_id = request.data.get('recommendation_id')
        action = request.data.get('action', 'viewed')

        try:
            recommendation = Recommendation.objects.get(id=recommendation_id, user=request.user)
            history = RecommendationHistory.objects.create(
                user=request.user,
                recommendation=recommendation,
                action=action
            )
            serializer = RecommendationHistorySerializer(history)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Recommendation.DoesNotExist:
            return Response({'error': 'Recommendation not found'}, status=status.HTTP_404_NOT_FOUND)
