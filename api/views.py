from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from pets.models import Pet, AdoptionRequest, Favorite
from .serializers import (
    PetSerializer, 
    AdoptionRequestSerializer, 
    FavoriteSerializer,
    UserRegisterSerializer,
    UserSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class PetViewSet(viewsets.ModelViewSet):
    """
    Pet API:
    GET /api/pets/ (supports pagination, search, and filtering)
    GET /api/pets/<id>/
    POST /api/pets/ (admin only)
    PUT /api/pets/<id>/ (admin only)
    DELETE /api/pets/<id>/ (admin only)
    """
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['animal_type', 'gender', 'location', 'status', 'breed', 'size', 'energy_level']
    search_fields = ['name', 'breed', 'location', 'description']
    ordering_fields = ['created_at', 'age', 'name']
    ordering = ['-created_at']


class AdoptionRequestViewSet(viewsets.ModelViewSet):
    """
    Adoption API:
    GET /api/adoptions/ (Users only see their own requests; admins see all)
    POST /api/adoptions/ (Enforces Rule 1 and Rule 2)
    GET /api/adoptions/<id>/
    PUT /api/adoptions/<id>/
    """
    serializer_class = AdoptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'pet__animal_type']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AdoptionRequest.objects.all().select_related('user', 'pet')
        return AdoptionRequest.objects.filter(user=user).select_related('user', 'pet')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Favorite API:
    GET /api/favorites/ (List authenticated user's favorites)
    POST /api/favorites/<id>/toggle/ (Toggle favorite status for pet ID)
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('pet')

    @action(detail=False, methods=['post'], url_path='toggle/(?P<pet_id>[^/.]+)')
    def toggle_favorite(self, request, pet_id=None):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({'error': 'Pet not found.'}, status=status.HTTP_404_NOT_FOUND)

        fav = Favorite.objects.filter(user=request.user, pet=pet).first()
        if fav:
            fav.delete()
            return Response({'favorited': False, 'message': f"Removed {pet.name} from favorites."})
        else:
            Favorite.objects.create(user=request.user, pet=pet)
            return Response({'favorited': True, 'message': f"Added {pet.name} to favorites!"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_api(request):
    """API endpoint for user registration; returns auth token."""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'User registered successfully',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    """API endpoint for login; returns auth token."""
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_api(request):
    """API endpoint to get current authenticated user info and stats."""
    user = request.user
    token, _ = Token.objects.get_or_create(user=user)
    total_apps = AdoptionRequest.objects.filter(user=user).count()
    fav_count = Favorite.objects.filter(user=user).count()

    return Response({
        'user': UserSerializer(user).data,
        'token': token.key,
        'stats': {
            'total_applications': total_apps,
            'total_favorites': fav_count,
        }
    })
