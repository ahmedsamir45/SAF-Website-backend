from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from rest_framework import permissions

from .views import (
    ProgramViewSet, ProgramImageViewSet, FavoriteViewSet, UserViewSet, 
    MessageContactViewSet, ProgramCategoriesView
)
from .blog_views import (
    CategoryViewSet, BlogPostViewSet, 
    NewsletterSubscriptionViewSet
)
from .serializers import CustomTokenObtainPairSerializer

# Main router
router = DefaultRouter()

# User management
router.register(r'users', UserViewSet, basename='user')

# Program management
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'blog-posts', BlogPostViewSet, basename='blogpost')
router.register(r'messages', MessageContactViewSet, basename='message')

# Newsletter subscription endpoints
newsletter_router = DefaultRouter()
newsletter_router.register(r'subscriptions', NewsletterSubscriptionViewSet, 
                         basename='newslettersubscription')

# Nested routers for programs and users
programs_router = routers.NestedSimpleRouter(router, r'programs', lookup='program')
programs_router.register(r'images', ProgramImageViewSet, basename='program-image')

users_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
users_router.register(r'favorites', FavoriteViewSet, basename='user-favorite')

# Program favorite endpoints
program_favorite_urls = [
    path('<int:pk>/favorite/', ProgramViewSet.as_view({'post': 'favorite'}), name='program-favorite'),
    path('<int:pk>/is_favorite/', ProgramViewSet.as_view({'get': 'is_favorite'}), name='program-is-favorite'),
    path('favorites/ids/', ProgramViewSet.as_view({'get': 'favorites_ids'}), name='program-favorites-ids'),
]

# Newsletter subscription endpoints
newsletter_subscription_urls = [
    path('', NewsletterSubscriptionViewSet.as_view({'get': 'list', 'post': 'create'}), name='newsletter-list'),
    path('<str:email>/', NewsletterSubscriptionViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
        'put': 'update',
        'patch': 'partial_update'
    }), name='newsletter-detail'),
    path('<str:email>/status/', NewsletterSubscriptionViewSet.as_view({'get': 'status'}), name='newsletter-status'),
    path('<str:email>/unsubscribe/', NewsletterSubscriptionViewSet.as_view({'post': 'unsubscribe'}), name='newsletter-unsubscribe'),
    path('activate/<str:email>/', NewsletterSubscriptionViewSet.as_view({'post': 'activate'}), name='newsletter-activate'),
]

# Main URL patterns
urlpatterns = [
    # Public program categories view
    path('public/programs/categories/', ProgramCategoriesView.as_view(), name='program-categories-public'),
    
    # Include all router URLs
    path('', include(router.urls)),
    path('', include(programs_router.urls)),
    path('', include(users_router.urls)),
    
    # Program favorites
    path('programs/', include(program_favorite_urls)),
    
    # Newsletter endpoints
    path('newsletter-subscriptions/', include(newsletter_subscription_urls)),
    
    # Contact form
    path('contact/', MessageContactViewSet.as_view({'post': 'create'}), name='contact'),
    
    # Health check endpoint
    path('health/', lambda request: Response({'status': 'ok'}), name='health-check'),
]

# Add all router URLs
urlpatterns += [
    path('', include(router.urls)),
    path('', include(programs_router.urls)),
    path('', include(users_router.urls)),
    
    # JWT Authentication with custom serializer
    path('auth/token/', 
         TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), 
         name='token_obtain_pair'),
    path('auth/token/refresh/', 
         TokenRefreshView.as_view(), 
         name='token_refresh'),
    path('auth/token/verify/', 
         TokenVerifyView.as_view(), 
         name='token_verify'),
    path('auth/token/blacklist/', 
         TokenBlacklistView.as_view(), 
         name='token_blacklist'),
    
    # Newsletter endpoints
    path('newsletter-subscriptions/<str:email>/status/', 
         NewsletterSubscriptionViewSet.as_view({'get': 'status'}), 
         name='newsletter-status'),
    
    # Program actions
    path('programs/featured/', 
         ProgramViewSet.as_view({'get': 'featured'}), 
         name='program-featured'),
    path('programs/enrolled/', 
         ProgramViewSet.as_view({'get': 'enrolled'}), 
         name='program-enrolled'),
    path('programs/categories/', 
         ProgramViewSet.as_view({'get': 'categories'}), 
         name='program-categories'),
         
    # Blog post actions
    path('blog/posts/<slug:slug>/publish/', 
         BlogPostViewSet.as_view({'post': 'publish'}), 
         name='blog-post-publish'),
    path('blog/posts/<slug:slug>/views/', 
         BlogPostViewSet.as_view({'post': 'increment_views'}), 
         name='blog-post-increment-views'),
]