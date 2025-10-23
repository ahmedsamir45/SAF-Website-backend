"""
Serializers for blog-related models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, BlogPost, NewsletterSubscription

User = get_user_model()  # Get the custom User model
from .serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'is_active']
        read_only_fields = ['id', 'slug']


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for listing blog posts (with limited fields)."""
    author = serializers.StringRelatedField()
    categories = CategorySerializer(many=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='blog:post-detail',
        lookup_field='slug',
        lookup_url_kwarg='slug'
    )

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'categories',
            'featured_image', 'published_at', 'view_count', 'url'
        ]
        read_only_fields = ['id', 'slug', 'published_at', 'view_count']


class BlogPostDetailSerializer(BlogPostListSerializer):
    """Serializer for detailed blog post view."""
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + [
            'content', 'status', 'allow_comments', 'seo_title',
            'seo_description', 'seo_keywords', 'created_at', 'updated_at'
        ]
        read_only_fields = BlogPostListSerializer.Meta.read_only_fields + [
            'created_at', 'updated_at'
        ]


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating blog posts."""
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.filter(is_active=True),
        required=False
    )
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'categories', 'featured_image',
            'status', 'allow_comments', 'seo_title', 'seo_description',
            'seo_keywords'
        ]

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        blog_post = BlogPost.objects.create(**validated_data)
        blog_post.categories.set(categories)
        return blog_post

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        instance = super().update(instance, validated_data)
        if categories is not None:
            instance.categories.set(categories)
        return instance


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for newsletter subscriptions."""
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'is_active', 'created_at']
        read_only_fields = ['is_active', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value
    
    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    def create(self, validated_data):
        # Remove password2 from the data before creating the user
        validated_data.pop('password2', None)
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user


class NewsletterConfirmSerializer(serializers.Serializer):
    """Serializer for confirming newsletter subscriptions."""
    email = serializers.EmailField()
    confirmation_code = serializers.UUIDField()

    def validate(self, data):
        try:
            subscription = NewsletterSubscription.objects.get(
                email=data['email'],
                confirmation_code=data['confirmation_code'],
                is_active=False
            )
        except NewsletterSubscription.DoesNotExist:
            raise serializers.ValidationError("Invalid confirmation code or email.")
        
        data['subscription'] = subscription
        return data
