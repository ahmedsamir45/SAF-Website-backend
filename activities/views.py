from django.conf import settings
from django.core.mail import send_mail
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import User, Program, ProgramImage, Favorite, ContactMessage
from .serializers import (
    UserSerializer,
    ProgramSerializer,
    ProgramImageSerializer,
    FavoriteSerializer,
    MessageContactSerializer,
    UserCreateWithProfileSerializer
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.AllowAny]  # Allow any for registration

    def get_permissions(self):
        if self.action in ['create', 'options']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['me']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateWithProfileSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Get or update the current user's profile.
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method in ['PUT', 'PATCH']:
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all().order_by('-post_date')  # Default ordering
    serializer_class = ProgramSerializer
    ordering_fields = ['post_date', 'start_date', 'end_date', 'title']
    ordering = ['-post_date']  # Default ordering
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        program = serializer.save()
        
        # Handle requirements if provided
        requirements_data = request.data.get('requirements', [])
        if requirements_data and isinstance(requirements_data, list):
            program.requirements.set(requirements_data)
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        program = serializer.save()
        
        # Handle requirements if provided
        if 'requirements' in request.data:
            requirements_data = request.data.get('requirements', [])
            if isinstance(requirements_data, list):
                program.requirements.set(requirements_data)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        program = self.get_object()
        user = request.user
        
        # Check if already favorited
        favorite = Favorite.objects.filter(user=user, program=program).first()
        
        if favorite:
            # If already favorited, remove from favorites (unfavorite)
            favorite.delete()
            return Response({'status': 'removed from favorites'}, status=status.HTTP_200_OK)
        else:
            # If not favorited, add to favorites
            Favorite.objects.create(user=user, program=program)
            return Response({'status': 'added to favorites'}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def is_favorite(self, request, pk=None):
        program = self.get_object()
        is_favorite = Favorite.objects.filter(
            user=request.user, 
            program=program
        ).exists()
        return Response({'is_favorite': is_favorite})  # Default ordering
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Public access is allowed for all read-only actions (list, retrieve, featured, categories).
        Write operations require authentication.
        """
        # Allow public access to list, retrieve, featured, and categories actions
        if self.action in ['list', 'retrieve', 'featured', 'categories']:
            return [permissions.AllowAny()]
            
        # Require authentication for write operations and enrolled action
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'enrolled']:
            return [permissions.IsAuthenticated()]
            
        # Default to requiring authentication for any other actions
        return [permissions.IsAuthenticated()]
        
    def get_queryset(self):
        """
        Return a properly ordered queryset.
        """
        queryset = super().get_queryset()
        # Ensure we have a consistent order to avoid pagination warnings
        if not queryset.ordered:
            queryset = queryset.order_by('-post_date')
        return queryset
        
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get a list of featured programs."""
        featured = self.get_queryset().filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def enrolled(self, request):
        """Return a list of programs the current user is enrolled in."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # For now, return an empty list
        # You can implement the actual logic here later
        return Response([], status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get a list of all program categories with counts."""
        categories = Program.objects.values_list('category', flat=True).distinct()
        categories_with_counts = []
        for category in categories:
            if category:  # Only include non-empty categories
                count = Program.objects.filter(category=category).count()
                categories_with_counts.append({
                    'name': category,
                    'count': count
                })
        return Response(categories_with_counts)
        
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites_ids(self, request):
        """Get a list of IDs of programs favorited by the current user."""
        favorite_ids = Favorite.objects.filter(
            user=request.user
        ).values_list('program_id', flat=True)
        return Response([{'program': pid} for pid in favorite_ids])
        

class ProgramCategoriesView(APIView):
    """
    Public endpoints for program categories and related data.
    These endpoints do not require authentication.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Get a list of all program categories with counts.
        This endpoint is publicly accessible and does not require authentication.
        """
        from django.db.models import Count
        try:
            # Get distinct categories with counts
            categories = Program.objects.values('category').annotate(
                count=Count('id')
            ).order_by('category')
            
            return Response(list(categories), status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch categories', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Handle different actions based on the 'action' parameter.
        Available actions: featured, enrolled, search
        """
        action = request.data.get('action')
        
        if action == 'featured':
            return self.get_featured(request)
        elif action == 'enrolled':
            return self.get_enrolled(request)
        elif action == 'search':
            return self.search_programs(request)
        else:
            return Response(
                {'error': 'Invalid action'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get_featured(self, request):
        """Get a list of featured programs."""
        try:
            featured = Program.objects.filter(is_featured=True).order_by('-created_at')[:6]
            serializer = ProgramSerializer(featured, many=True)
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch featured programs', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_enrolled(self, request):
        """Return a list of programs the current user is enrolled in."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # For now, return an empty list
        return Response({
            'status': 'success',
            'data': []
        }, status=status.HTTP_200_OK)
    
    def search_programs(self, request):
        """Search programs with optional filters."""
        query = request.data.get('q', '')
        try:
            programs = Program.objects.all()
            
            # Apply search query
            if query:
                programs = programs.filter(
                    Q(title__icontains=query) | 
                    Q(description__icontains=query)
                )
            
            # Apply filters
            filters = {}
            filter_fields = ['category', 'type', 'audience', 'kind']
            
            for field in filter_fields:
                value = request.data.get(field)
                if value:
                    filters[field] = value
            
            if filters:
                programs = programs.filter(**filters)
            
            serializer = ProgramSerializer(programs, many=True)
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Search failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProgramImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramImageSerializer
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Return empty queryset for schema generation
            return ProgramImage.objects.none()
        return ProgramImage.objects.filter(program_id=self.kwargs['program_pk'])

    def perform_create(self, serializer):
        program = get_object_or_404(Program, pk=self.kwargs['program_pk'])
        serializer.save(program=program)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()  # Return empty queryset for schema generation
        return Favorite.objects.filter(user_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        user = get_object_or_404(User, pk=self.kwargs['user_pk'])
        if user != self.request.user:
            raise permissions.PermissionDenied("You can only add favorites to your own account")
        serializer.save(user=user)

class MessageContactViewSet(viewsets.GenericViewSet):
    """
    ViewSet for handling contact form submissions.
    Anyone can submit a contact message, but only admins can view/update/delete them.
    """
    queryset = ContactMessage.objects.all()
    serializer_class = MessageContactSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.AllowAny()]
    
    def create(self, request, *args, **kwargs):
        """Handle contact form submission."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'status': 'error',
                    'errors': serializer.errors,
                    'message': 'Please correct the errors below.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save the message
            message = serializer.save()
            
            # Send notification email (if configured)
            self._send_notification_email(message)
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Your message has been sent successfully!',
                    'data': {
                        'id': message.id,
                        'name': message.name,
                        'email': message.email,
                        'subject': message.subject,
                        'created_at': message.created_at
                    }
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing contact form: {str(e)}")
            
            return Response(
                {
                    'status': 'error',
                    'message': 'An error occurred while processing your message. Please try again later.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _send_notification_email(self, message):
        """Send notification email to admin about new contact message."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not hasattr(settings, 'ADMIN_EMAIL') or not settings.ADMIN_EMAIL:
                logger.warning('ADMIN_EMAIL not set in settings. Email notification not sent.')
                return
                
            if not hasattr(settings, 'DEFAULT_FROM_EMAIL') or not settings.DEFAULT_FROM_EMAIL:
                logger.warning('DEFAULT_FROM_EMAIL not set in settings. Email notification not sent.')
                return
                
            subject = f"New Contact Message: {message.subject}"
            body = f"""
            New contact form submission:
            
            Name: {message.name}
            Email: {message.email}
            
            Subject: {message.subject}
            
            Message:
            {message.message}
            
            ---
            This is an automated message.
            """
            
            logger.info(f"Attempting to send email to {settings.ADMIN_EMAIL} from {settings.DEFAULT_FROM_EMAIL}")
            logger.debug(f"Email settings - Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}, Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
            
            send_mail(
                subject=subject,
                message=body.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False  # Set to False to see any SMTP errors
            )
            logger.info("Email sent successfully")
            
        except Exception as e:
            # Log the error with detailed information
            logger.error(f"Failed to send contact form notification: {str(e)}", exc_info=True)
            logger.error(f"Failed to send contact form notification: {str(e)}")