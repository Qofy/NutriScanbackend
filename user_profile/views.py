from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import UserHealthProfile, DailyTracking, SavedFood
from .serializers import UserHealthProfileSerializer, DailyTrackingSerializer, SavedFoodSerializer, UserSerializer

class UserHealthProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def retrieve(self, request):
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
            serializer = UserHealthProfileSerializer(profile)
            return Response(serializer.data)
        except UserHealthProfile.DoesNotExist:
            return Response({'error': 'Health profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
            serializer = UserHealthProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserHealthProfile.DoesNotExist:
            return Response({'error': 'Health profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def create_profile(self, request):
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
            return Response({'error': 'Profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except UserHealthProfile.DoesNotExist:
            serializer = UserHealthProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_health_conditions(self, request):
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
            conditions = request.data.get('conditions', [])
            profile.health_conditions = conditions
            profile.save()
            serializer = UserHealthProfileSerializer(profile)
            return Response(serializer.data)
        except UserHealthProfile.DoesNotExist:
            return Response({'error': 'Health profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def update_allergies(self, request):
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
            allergens = request.data.get('allergens', [])
            profile.allergies = allergens
            profile.save()
            serializer = UserHealthProfileSerializer(profile)
            return Response(serializer.data)
        except UserHealthProfile.DoesNotExist:
            return Response({'error': 'Health profile not found'}, status=status.HTTP_404_NOT_FOUND)


class DailyTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = DailyTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return DailyTracking.objects.filter(user=self.request.user)
        return DailyTracking.objects.none()

    def create(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = DailyTrackingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def today(self, request):
        from datetime import date
        try:
            tracking = DailyTracking.objects.get(user=request.user, date=date.today())
            serializer = DailyTrackingSerializer(tracking)
            return Response(serializer.data)
        except DailyTracking.DoesNotExist:
            return Response({'message': 'No tracking data for today'}, status=status.HTTP_404_NOT_FOUND)


class SavedFoodViewSet(viewsets.ModelViewSet):
    serializer_class = SavedFoodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return SavedFood.objects.filter(user=self.request.user)
        return SavedFood.objects.none()

    def create(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = SavedFoodSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query required'}, status=status.HTTP_400_BAD_REQUEST)

        saved_foods = self.get_queryset().filter(food_name__icontains=query)
        serializer = SavedFoodSerializer(saved_foods, many=True)
        return Response(serializer.data)


class CurrentUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
