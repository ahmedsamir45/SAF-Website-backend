"""
Views for blog and newsletter functionality.
"""
import uuid
import logging
from datetime import timedelta
from rest_framework import (
    viewsets, mixins, permissions, status, exceptions
)
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.urls import reverse
from django.db import transaction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ACTIVATION_EXPIRY_HOURS = 24  # Activation link expiry time in hours

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


from .throttles import NewsletterSubscriptionThrottle

@permission_classes([AllowAny])
class NewsletterSubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing newsletter subscriptions with email verification.
    - Allows unauthenticated users to subscribe with email verification
    - Implements rate limiting to prevent abuse
    - Handles subscription activation via unique links
    """
    serializer_class = NewsletterSubscriptionSerializer
    lookup_field = 'email'
    throttle_classes = [NewsletterSubscriptionThrottle]

    def get_queryset(self):
        # Only allow users to see their own subscription or all for admins
        if self.request.user.is_staff:
            return NewsletterSubscription.objects.all()
        return NewsletterSubscription.objects.none()  # Regular users can't list subscriptions

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context.update({
            'request': self.request,
            'ip_address': self.get_client_ip(),
            'user_agent': self.request.META.get('HTTP_USER_AGENT', '')
        })
        return context

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Handle newsletter subscription with email verification.
        - Validates email format
        - Prevents duplicate subscriptions
        - Sends verification email with unique activation link
        - Implements atomic transaction for data consistency
        """
        email = request.data.get('email', '').strip().lower()
        
        # Validate email
        if not email or '@' not in email:
            return Response(
                {
                    'status': 'error',
                    'message': 'A valid email address is required.',
                    'errors': {'email': ['This field must be a valid email address.']}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Check for existing subscription
            subscription, created = NewsletterSubscription.objects.get_or_create(
                email=email,
                defaults={
                    'activation_code': str(uuid.uuid4()),
                    'activation_sent_at': timezone.now(),
                    'is_active': False,
                    'ip_address': self.get_client_ip(),
                }
            )
            
            # If subscription exists and is active
            if not created and subscription.is_active:
                return Response(
                    {
                        'status': 'success',
                        'message': 'You are already subscribed to our newsletter!',
                        'data': {
                            'email': email,
                            'is_active': True,
                            'already_subscribed': True
                        }
                    },
                    status=status.HTTP_200_OK
                )
            
            # Update activation code for existing inactive subscription
            if not created:
                subscription.activation_code = str(uuid.uuid4())
                subscription.activation_sent_at = timezone.now()
                subscription.save(update_fields=['activation_code', 'activation_sent_at'])
            
            # Build activation URL
            activation_path = reverse('newsletter-activate', kwargs={
                'email': subscription.email,
                'activation_code': str(subscription.activation_code)
            })
            activation_url = request.build_absolute_uri(activation_path)
            
            # Send activation email
            try:
                send_mail(
                    subject='Activate Your Newsletter Subscription',
                    message=f'''
                    Thank you for subscribing to our newsletter!
                    
                    Please click the following link to confirm your subscription:
                    {activation_url}
                    
                    This link will expire in {ACTIVATION_EXPIRY_HOURS} hours.
                    
                    If you did not request this, please ignore this email.
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                logger.info(f"Activation email sent to {email}")
                
                return Response(
                    {
                        'status': 'success',
                        'message': 'Please check your email to activate your subscription.',
                        'data': {
                            'email': email,
                            'is_active': False,
                            'activation_sent': True
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
                
            except Exception as e:
                logger.error(f"Failed to send activation email to {email}: {str(e)}")
                if created:  # Only delete if we just created this record
                    subscription.delete()
                
                return Response(
                    {
                        'status': 'error',
                        'message': 'Failed to send activation email. Please try again later.',
                        'errors': {'email': ['Failed to send activation email.']}
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
    
    @action(detail=True, methods=['get'])
    @permission_classes([AllowAny])
    def status(self, request, email=None):
        """
        Check subscription status for an email.
        - Public endpoint (no authentication required)
        - Returns minimal information for privacy
        """
        if not email or '@' not in email:
            return Response(
                {'error': 'Valid email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            subscription = NewsletterSubscription.objects.get(email=email.lower())
            return Response({
                'email': subscription.email,
                'is_active': subscription.is_active,
                'subscribed_at': subscription.created_at.isoformat() if subscription.created_at else None
            })
        except NewsletterSubscription.DoesNotExist:
            return Response({
                'email': email,
                'is_active': False,
                'message': 'No active subscription found for this email.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    @permission_classes([AllowAny])
    def unsubscribe(self, request, email=None):
        """
        Unsubscribe from the newsletter.
        - Public endpoint (no authentication required)
        - Implements idempotent unsubscription
        """
        if not email or '@' not in email:
            return Response(
                {'error': 'Valid email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            subscription = NewsletterSubscription.objects.get(
                email=email.lower(),
                is_active=True  # Only unsubscribe active subscriptions
            )
            
            subscription.unsubscribe()  # Using the model method
            
            return Response({
                'status': 'success',
                'message': 'You have been unsubscribed from our newsletter.',
                'data': {
                    'email': email,
                    'is_active': False,
                    'unsubscribed_at': subscription.unsubscribed_at.isoformat()
                }
            })
            
        except NewsletterSubscription.DoesNotExist:
            # Return success even if already unsubscribed or never subscribed
            return Response({
                'status': 'success',
                'message': 'No active subscription found for this email.',
                'email': email,
                'is_active': False
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], 
             url_path='activate/(?P<email>[^/.]+)/(?P<activation_code>[^/.]+)')
    @permission_classes([AllowAny])
    def activate(self, request, email=None, activation_code=None):
        """
        Activate a newsletter subscription using the activation code.
        - Public endpoint (no authentication required)
        - Handles activation code expiration
        - Implements one-time use of activation codes
        """
        if not all([email, activation_code]) or '@' not in email:
            return Response(
                {
                    'status': 'error',
                    'message': 'Valid email and activation code are required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Use select_for_update to prevent race conditions
                subscription = NewsletterSubscription.objects.select_for_update().get(
                    email=email.lower(),
                    activation_code=activation_code,
                    is_active=False
                )
                
                # Check if activation code is expired
                expiry_time = subscription.activation_sent_at + timedelta(hours=ACTIVATION_EXPIRY_HOURS)
                if timezone.now() > expiry_time:
                    # Delete expired subscription to clean up
                    subscription.delete()
                    return Response(
                        {
                            'status': 'error',
                            'message': 'Activation link has expired. Please subscribe again.',
                            'email': email
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Activate the subscription
                subscription.is_active = True
                subscription.activated_at = timezone.now()
                subscription.activation_code = None  # Invalidate the code after use
                subscription.save(update_fields=[
                    'is_active', 
                    'activated_at', 
                    'activation_code',
                    'updated_at'
                ])
                
                logger.info(f"Activated subscription for {email}")
                
                # Redirect to success page or return success response
                return Response(
                    {
                        'status': 'success',
                        'message': 'Your subscription has been activated successfully!',
                        'data': {
                            'email': email,
                            'is_active': True,
                            'activated_at': subscription.activated_at.isoformat()
                        }
                    },
                    status=status.HTTP_200_OK
                )
                
        except NewsletterSubscription.DoesNotExist:
            logger.warning(f"Invalid activation attempt for {email}")
            return Response(
                {
                    'status': 'error',
                    'message': 'Invalid or expired activation link. Please request a new one.',
                    'email': email
                },
                status=status.HTTP_404_NOT_FOUND
            )
            
        except Exception as e:
            logger.error(f"Error activating subscription for {email}: {str(e)}")
            return Response(
                {
                    'status': 'error',
                    'message': 'An error occurred while activating your subscription. Please try again.',
                    'email': email
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self):
        """
        Get the client's IP address.
        Handles various proxy headers and returns the most reliable IP.
        """
        # Standard headers used by proxies to forward the client IP
        proxy_headers = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CLIENT_IP',
            'REMOTE_ADDR',
        ]
        
        for header in proxy_headers:
            if header in self.request.META:
                # Get the first IP in case of multiple IPs (common with X-Forwarded-For)
                ip = self.request.META[header].split(',')[0].strip()
                if ip:
                    return ip
        
        return '0.0.0.0'  # Default if no IP found