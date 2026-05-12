from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import FoodAnalysis, FoodItem
from .serializers import FoodAnalysisSerializer, FoodItemSerializer, FoodAnalysisListSerializer
from .yolo_service import yolo_detector
from .nutrition_service import get_nutritional_info, evaluate_safety
from .yolo_trainer import run_training_async, get_training_status
import logging
import json

logger = logging.getLogger(__name__)

class FoodAnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = FoodAnalysisSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return FoodAnalysis.objects.filter(user=self.request.user)
        return FoodAnalysis.objects.none()

    @action(detail=False, methods=['post'])
    def manual_analyze(self, request):
        try:
            # Parse food_items from form data (JSON string or direct)
            food_items_data = request.data.get('food_items', [])
            if isinstance(food_items_data, str):
                food_items = json.loads(food_items_data)
            else:
                food_items = food_items_data

            if not food_items:
                return Response({'error': 'No food items provided'}, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"🔍 Starting manual food analysis for {len(food_items)} items")

            nutritional_info = get_nutritional_info(food_items)
            logger.info(f"✓ Got nutrition data")

            # Get health profile from request (passed from frontend)
            user_health_profile = request.data.get('health_profile', {})
            if isinstance(user_health_profile, str):
                try:
                    user_health_profile = json.loads(user_health_profile)
                except:
                    user_health_profile = {}

            # If no health profile from request, try to get from user's profile settings
            if (not user_health_profile or not user_health_profile.get('conditions')) and request.user and request.user.is_authenticated:
                try:
                    from user_profile.models import UserHealthProfile
                    profile = UserHealthProfile.objects.get(user=request.user)
                    merged_conditions = list(user_health_profile.get('conditions', [])) if user_health_profile else []
                    merged_allergens = list(user_health_profile.get('allergens', [])) if user_health_profile else []

                    # Add from user profile settings
                    merged_conditions.extend(profile.health_conditions or [])
                    merged_allergens.extend(profile.allergies or [])

                    user_health_profile = {
                        'conditions': list(set(merged_conditions)),  # Remove duplicates
                        'allergens': list(set(merged_allergens))
                    }
                    logger.info(f"✓ Got health profile from user settings: {user_health_profile}")
                except:
                    pass

            safety_level, safety_reason = evaluate_safety(food_items, user_health_profile)
            logger.info(f"🛡️ Safety level: {safety_level}")

            user = request.user if request.user.is_authenticated else None

            # Get optional image from request
            image_file = request.FILES.get('image', None)

            food_analysis = FoodAnalysis.objects.create(
                user=user,
                image=image_file,
                recognized_items=food_items,
                nutritional_info=nutritional_info,
                safety_level=safety_level,
                confidence_score=1.0,
                is_manual=True,
                analysis_result={
                    'detection': {'detected_items': food_items, 'method': 'manual'},
                    'nutrition': nutritional_info,
                    'safety_reason': safety_reason
                }
            )

            logger.info(f"✓ Created food analysis: {food_analysis.id} (is_manual={food_analysis.is_manual})")

            # Trigger async YOLO training if image was provided
            if image_file:
                run_training_async()

            serializer = FoodAnalysisSerializer(food_analysis, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"❌ Manual analyze error: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def detect(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']
        detection_result = yolo_detector.detect_food(image_file)

        if not detection_result['success']:
            return Response({'detected': False, 'items': [], 'confidence_score': 0}, status=status.HTTP_200_OK)

        detected_items = detection_result['detected_items']
        return Response({
            'detected': len(detected_items) > 0,
            'items': detected_items,
            'confidence_score': detection_result['confidence_score']
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        try:
            if 'image' not in request.FILES:
                return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

            image_file = request.FILES['image']

            # Get health profile from request (passed from frontend)
            user_health_profile = request.data.get('health_profile', {})
            if isinstance(user_health_profile, str):
                import json
                try:
                    user_health_profile = json.loads(user_health_profile)
                except:
                    user_health_profile = {}

            # If no health profile from request, try to get from user's profile settings
            if (not user_health_profile or not user_health_profile.get('conditions')) and request.user and request.user.is_authenticated:
                try:
                    from user_profile.models import UserHealthProfile
                    profile = UserHealthProfile.objects.get(user=request.user)
                    merged_conditions = list(user_health_profile.get('conditions', [])) if user_health_profile else []
                    merged_allergens = list(user_health_profile.get('allergens', [])) if user_health_profile else []

                    # Add from user profile settings
                    merged_conditions.extend(profile.health_conditions or [])
                    merged_allergens.extend(profile.allergies or [])

                    user_health_profile = {
                        'conditions': list(set(merged_conditions)),  # Remove duplicates
                        'allergens': list(set(merged_allergens))
                    }
                    logger.info(f"✓ Got health profile from user settings: {user_health_profile}")
                except:
                    pass

            logger.info(f"🔍 Starting food detection for image: {image_file.name}")
            detection_result = yolo_detector.detect_food(image_file)

            if not detection_result['success']:
                logger.error(f"❌ Detection failed: {detection_result}")
                return Response({'error': 'Detection failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            recognized_items = detection_result['detected_items']
            logger.info(f"✓ Detected {len(recognized_items)} food items")

            logger.info(f"📊 Fetching nutritional info...")
            nutritional_info = get_nutritional_info(recognized_items)
            logger.info(f"✓ Got nutrition data")

            safety_level, safety_reason = evaluate_safety(recognized_items, user_health_profile)
            logger.info(f"🛡️ Safety level: {safety_level}")

            user = request.user if request.user.is_authenticated else None

            food_analysis = FoodAnalysis.objects.create(
                user=user,
                image=image_file,
                recognized_items=recognized_items,
                nutritional_info=nutritional_info,
                safety_level=safety_level,
                confidence_score=detection_result['confidence_score'],
                analysis_result={
                    'detection': detection_result,
                    'nutrition': nutritional_info,
                    'safety_reason': safety_reason
                }
            )

            logger.info(f"✓ Created food analysis: {food_analysis.id}")
            serializer = FoodAnalysisSerializer(food_analysis, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"❌ Analyze endpoint error: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def recent(self, request):
        limit = request.query_params.get('limit', 10)
        recent_analyses = self.get_queryset()[:int(limit)]
        serializer = FoodAnalysisListSerializer(recent_analyses, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def training_status(self, request):
        return Response(get_training_status())

    def destroy(self, request, pk=None):
        try:
            food_analysis = FoodAnalysis.objects.get(id=pk)
            food_analysis.delete()
            return Response({'success': True, 'message': 'Analysis deleted'}, status=status.HTTP_204_NO_CONTENT)
        except FoodAnalysis.DoesNotExist:
            return Response({'error': 'Analysis not found'}, status=status.HTTP_404_NOT_FOUND)

class FoodItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query required'}, status=status.HTTP_400_BAD_REQUEST)

        foods = FoodItem.objects.filter(name__icontains=query)
        serializer = FoodItemSerializer(foods, many=True)
        return Response(serializer.data)
