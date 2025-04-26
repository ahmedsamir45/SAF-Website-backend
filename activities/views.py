from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import User, Program, ProgramImage, Favorite, MessageContact
from .serializer import (
    UserSerializer,
    ProgramSerializer,
    ProgramImageSerializer,
    FavoriteSerializer,
    MessageContactSerializer,
    UserCreateWithProfileSerializer
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy', 'list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateWithProfileSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]


    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'category', 'audience', 'kind', 'target_academic']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'cost', 'post_date']

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def search(self, request):
        query = request.query_params.get('q', '')
        programs = Program.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
        
        # Apply filters
        category = request.query_params.get('category')
        if category:
            programs = programs.filter(category=category)
        
        # You can add more filters here
        program_type = request.query_params.get('type')
        if program_type:
            programs = programs.filter(type=program_type)
            
        audience = request.query_params.get('audience')
        if audience:
            programs = programs.filter(audience=audience)
        
        kind = request.query_params.get('kind')
        if kind:
            programs = programs.filter(kind=kind)
        
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        program = self.get_object()
        user = request.user

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(user=user, program=program)
            if created:
                serializer = FavoriteSerializer(favorite)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'detail': 'Already in favorites'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            favorite = get_object_or_404(Favorite, user=user, program=program)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class ProgramImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramImageSerializer
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return ProgramImage.objects.filter(program_id=self.kwargs['program_pk'])

    def perform_create(self, serializer):
        program = get_object_or_404(Program, pk=self.kwargs['program_pk'])
        serializer.save(program=program)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        user = get_object_or_404(User, pk=self.kwargs['user_pk'])
        if user != self.request.user:
            raise permissions.PermissionDenied("You can only add favorites to your own account")
        serializer.save(user=user)

class MessageContactViewSet(viewsets.ModelViewSet):
    queryset = MessageContact.objects.all()
    serializer_class = MessageContactSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to send messages

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.AllowAny()]