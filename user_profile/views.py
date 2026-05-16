from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserHealthProfile, DailyTracking, SavedFood
from .serializers import UserHealthProfileSerializer, DailyTrackingSerializer, SavedFoodSerializer, UserSerializer

class UserHealthProfileViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def retrieve(self, request):
        try:
            profile, created = UserHealthProfile.objects.get_or_create(user=request.user)
            serializer = UserHealthProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        try:
            profile, created = UserHealthProfile.objects.get_or_create(user=request.user)
            serializer = UserHealthProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not username or not email or not password:
            return Response({'error': 'Username, email, and password required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({'error': 'Password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create health profile for new user
        UserHealthProfile.objects.get_or_create(user=user)

        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)

    permission_classes = [AllowAny]

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
