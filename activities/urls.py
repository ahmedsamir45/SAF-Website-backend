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
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

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
router.register(r'newsletter-subscriptions', NewsletterSubscriptionViewSet, 
               basename='newslettersubscription')
router.register(r'messages', MessageContactViewSet, basename='message')

# Nested routers for programs and users
programs_router = routers.NestedSimpleRouter(router, r'programs', lookup='program')
programs_router.register(r'images', ProgramImageViewSet, basename='program-image')

# Add favorite endpoints directly to urlpatterns
program_favorite_urls = [
    path('<int:pk>/favorite/', ProgramViewSet.as_view({'post': 'favorite'}), name='program-favorite'),
    path('<int:pk>/is_favorite/', ProgramViewSet.as_view({'get': 'is_favorite'}), name='program-is-favorite'),
    path('favorites/ids/', ProgramViewSet.as_view({'get': 'favorites_ids'}), name='program-favorites-ids'),
]


users_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
users_router.register(r'favorites', FavoriteViewSet, basename='user-favorite')

urlpatterns = [
    # Public program categories view
    path('public/programs/categories/', ProgramCategoriesView.as_view(), name='program-categories-public'),
    
    # Program favorite endpoints
    path('programs/', include(program_favorite_urls)),
    
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
    path('newsletter/confirm/', 
         NewsletterSubscriptionViewSet.as_view({'post': 'confirm'}), 
         name='newsletter-confirm'),
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