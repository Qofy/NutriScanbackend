from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Recommendation, RecommendationHistory
from .serializers import RecommendationSerializer, RecommendationHistorySerializer
from .engine import RecommendationEngine
from medical_processing.models import MedicalReport
from food_recognition.models import FoodAnalysis
import logging

logger = logging.getLogger(__name__)

class RecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = RecommendationSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
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
    def smart_generate(self, request):
        """
        Generate AI-powered personalized recommendations from user's food scans + medical reports
        """
        try:
            user = request.user if request.user.is_authenticated else None

            # Fetch user's food scans
            food_analyses = FoodAnalysis.objects.filter(user=user).order_by('-uploaded_at')[:10]
            recent_foods = [
                {
                    'name': item.get('name', 'Unknown'),
                    'confidence': item.get('confidence', 0)
                }
                for analysis in food_analyses
                for item in analysis.recognized_items
            ] if food_analyses else []

            # Fetch user's medical reports (PRIMARY source)
            medical_reports = MedicalReport.objects.filter(user=user, status='completed')
            latest_medical_data = None  # Will use PRIMARY source for recommendations

            conditions = []
            allergens = []
            dietary_restrictions = []

            for report in medical_reports:
                # Use extracted_data from NLP
                if report.extracted_data:
                    # Store latest report's full extracted data as PRIMARY source
                    if not latest_medical_data:
                        latest_medical_data = report.extracted_data
                        logger.info(f"✓ Using medical report {report.id} as PRIMARY source for recommendations")

                    for condition in report.extracted_data.get('conditions', []):
                        if isinstance(condition, dict):
                            conditions.append(condition.get('condition', condition))
                        else:
                            conditions.append(condition)

                    for allergen in report.extracted_data.get('allergens', []):
                        if isinstance(allergen, dict):
                            allergens.append(allergen.get('allergen', allergen))
                        else:
                            allergens.append(allergen)

                    for restriction in report.extracted_data.get('dietary_restrictions', []):
                        if isinstance(restriction, dict):
                            dietary_restrictions.append(restriction.get('restriction', restriction))
                        else:
                            dietary_restrictions.append(restriction)

            # If no conditions from medical reports, try user profile settings
            user_country = None
            if not conditions and user:
                try:
                    from user_profile.models import UserHealthProfile
                    profile = UserHealthProfile.objects.get(user=user)
                    conditions = profile.health_conditions or []
                    allergens.extend(profile.allergies or [])
                    dietary_restrictions.extend(profile.dietary_restrictions or [])
                    user_country = profile.country
                    logger.info(f"✓ Got health profile from user settings")
                except:
                    pass
            elif user:
                # Get country from user profile even if conditions came from medical reports
                try:
                    from user_profile.models import UserHealthProfile
                    profile = UserHealthProfile.objects.get(user=user)
                    user_country = profile.country
                except:
                    pass

            # Build health profile
            health_profile = {
                'conditions': list(set(conditions)),
                'allergens': list(set(allergens)),
                'dietary_restrictions': list(set(dietary_restrictions))
            }

            food_history = {
                'recent_foods': recent_foods
            }

            logger.info(f"🔍 Generating smart recommendations")
            logger.info(f"  PRIMARY source: Medical report data" if latest_medical_data else "  PRIMARY source: User health profile")
            logger.info(f"  SECONDARY source: Food scan history ({len(recent_foods)} foods)")
            if user_country:
                logger.info(f"  TERTIARY source: Country-based recommendations ({user_country})")

            # Generate AI recommendations with medical data as PRIMARY source
            ai_recommendations = RecommendationEngine.generate_ai_recommendations(
                health_profile,
                food_history,
                extracted_medical_data=latest_medical_data,
                user_country=user_country
            )

            # Save recommendations to database
            created_recommendations = []
            for rec in ai_recommendations:
                # Get condition from AI response
                rec_condition = rec.get('condition', 'general')

                # Validate that condition is one of user's actual conditions
                # If not, use the first user condition as fallback
                user_conditions = health_profile.get('conditions', [])
                if user_conditions and rec_condition.lower() not in [c.lower() for c in user_conditions]:
                    rec_condition = user_conditions[0]
                elif not user_conditions:
                    rec_condition = 'general'

                recommendation_obj = Recommendation.objects.create(
                    user=user,
                    food_item=rec.get('food_item', 'Unknown'),
                    description=rec.get('description', ''),
                    condition=rec_condition,
                    benefit=rec.get('benefit', ''),
                    severity=rec.get('severity', 'safe'),
                    nutritional_info=rec.get('nutritional_info', {}),
                    based_on_food_analysis=bool(recent_foods),
                    based_on_medical_report=bool(medical_reports)
                )
                created_recommendations.append(recommendation_obj)

            logger.info(f"✅ Created {len(created_recommendations)} smart recommendations")
            serializer = RecommendationSerializer(created_recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"❌ Smart generate error: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to generate recommendations: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
