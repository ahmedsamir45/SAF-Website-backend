"""
Views for blog and newsletter functionality.
"""
import uuid
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Category, BlogPost, NewsletterSubscription
from .blog_serializers import (
    CategorySerializer,
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostCreateUpdateSerializer,
    NewsletterSubscriptionSerializer,
    NewsletterConfirmSerializer
)


User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog post categories.
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts.
    """
    queryset = BlogPost.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostCreateUpdateSerializer
    
    def get_queryset(self):
        queryset = BlogPost.objects.all()
        
        # Filter by status for non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                status='published',
                published_at__lte=timezone.now()
            )
        
        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
            
        # Filter by author
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
            
        return queryset.select_related('author').prefetch_related('categories')
    
    def perform_create(self, serializer):
        # Set the author to the current user
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):
        """Publish a draft blog post."""
        blog_post = self.get_object()
        if blog_post.status != 'draft':
            return Response(
                {'detail': 'Only draft posts can be published.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        blog_post.status = 'published'
        blog_post.published_at = timezone.now()
        blog_post.save()
        
        serializer = self.get_serializer(blog_post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, slug=None):
        """Increment the view count for a blog post."""
        blog_post = self.get_object()
        blog_post.view_count += 1
        blog_post.save()
        return Response({'view_count': blog_post.view_count})


class NewsletterSubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing newsletter subscriptions.
    Allows unauthenticated users to subscribe to the newsletter.
    """
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated subscriptions
    lookup_field = 'email'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return NewsletterSubscription.objects.all()
        # For non-staff users, only allow access to their own subscription
        if self.request.user.is_authenticated:
            return NewsletterSubscription.objects.filter(email=self.request.user.email)
        return NewsletterSubscription.objects.none()
    
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        """Handle newsletter subscription."""
        email = request.data.get('email', '').strip().lower()
        
        # Validate email
        if not email:
            return Response(
                {
                    'status': 'error',
                    'message': 'Email is required.',
                    'field_errors': {'email': ['This field is required.']}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Simple email validation
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {
                    'status': 'error',
                    'message': 'Please enter a valid email address.',
                    'field_errors': {'email': ['Enter a valid email address.']}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already subscribed and active
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            if subscription.is_active:
                return Response(
                    {
                        'status': 'success',
                        'message': 'You are already subscribed to our newsletter.',
                        'data': {'email': email, 'is_active': True}
                    },
                    status=status.HTTP_200_OK
                )
            
            # If exists but not active, update the subscription
            subscription.confirmation_code = uuid.uuid4()
            subscription.ip_address = self.get_client_ip()
            subscription.save(update_fields=['confirmation_code', 'ip_address'])
            
        except NewsletterSubscription.DoesNotExist:
            # Create new subscription
            subscription = NewsletterSubscription.objects.create(
                email=email,
                ip_address=self.get_client_ip(),
                is_active=False,
                confirmation_code=uuid.uuid4()
            )
        
        # Send confirmation email
        try:
            self.send_confirmation_email(subscription)
            return Response(
                {
                    'status': 'success',
                    'message': 'Confirmation email has been sent. Please check your inbox to confirm your subscription.',
                    'data': {'email': email, 'confirmation_sent': True}
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Log the error but don't fail the subscription
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send confirmation email to {email}: {str(e)}")
            
            # Still return success since we've saved the subscription
            return Response(
                {
                    'status': 'success',
                    'message': 'Subscription received, but we encountered an issue sending the confirmation email. You can request a new confirmation email later.',
                    'data': {
                        'email': email,
                        'confirmation_sent': False,
                        'needs_confirmation': True
                    }
                },
                status=status.HTTP_201_CREATED
            )
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """
        Confirm a newsletter subscription.
        Requires 'email' and 'confirmation_code' in the request data.
        """
        serializer = NewsletterConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'status': 'error',
                    'message': 'Invalid confirmation data.',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription = serializer.validated_data['subscription']
        
        # Check if already confirmed
        if subscription.is_active:
            return Response(
                {
                    'status': 'success',
                    'message': 'This subscription is already active.',
                    'data': {
                        'email': subscription.email,
                        'is_active': True,
                        'already_confirmed': True
                    }
                },
                status=status.HTTP_200_OK
            )
        
        # Confirm the subscription
        subscription.confirm()
        
        return Response(
            {
                'status': 'success',
                'message': 'Thank you for confirming your subscription!',
                'data': {
                    'email': subscription.email,
                    'is_active': True,
                    'confirmed_at': subscription.confirmed_at
                }
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def status(self, request, email=None):
        """Check subscription status for an email."""
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            return Response({
                'email': subscription.email,
                'is_active': subscription.is_active,
                'subscribed_at': subscription.created_at,
                'confirmed_at': subscription.confirmed_at
            })
        except NewsletterSubscription.DoesNotExist:
            return Response({
                'email': email,
                'is_active': False,
                'message': 'Email is not subscribed.'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, email=None):
        """Unsubscribe from the newsletter."""
        subscription = self.get_object()
        subscription.unsubscribe()
        return Response(
            {'detail': 'Successfully unsubscribed from the newsletter.'},
            status=status.HTTP_200_OK
        )
    
    def get_client_ip(self):
        """Get the client's IP address."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def send_confirmation_email(self, subscription):
        """Send a confirmation email to the subscriber."""
        subject = 'Confirm your newsletter subscription'
        
        # Get frontend URL from settings or use a default
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Create confirmation URL
        confirmation_url = (
            f"{frontend_url.rstrip('/')}/newsletter/confirm/"
            f"?email={subscription.email}&code={subscription.confirmation_code}"
        )
        
        message = (
            f"Thank you for subscribing to our newsletter!\n\n"
            f"Please confirm your subscription by clicking the following link:\n"
            f"{confirmation_url}\n\n"
            f"If you didn't subscribe, please ignore this email."
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscription.email],
            fail_silently=False,
        )