from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Program, ProgramImage, Favorite, ContactMessage, Requirement
from rest_framework.serializers import SerializerMethodField
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
        read_only_fields = ('is_active', 'is_staff')

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ['id', 'description']
        read_only_fields = ('id',)

class ProgramSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Program
        fields = [
            'id', 'title', 'description', 'cost', 'start_date', 'end_date', 
            'post_date', 'url', 'type', 'category', 'audience', 'kind', 
            'target_academic', 'image', 'image_url', 'is_featured', 'created_at', 
            'updated_at', 'requirements'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'image_url')
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                # In development, use request.build_absolute_uri
                if settings.DEBUG:
                    return request.build_absolute_uri(obj.image.url)
                # In production, use the full URL with the domain
                return f"{settings.BASE_URL}{obj.image.url}"
            # Fallback if no request is available
            return f"{settings.BASE_URL}{obj.image.url}"
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure requirements are included in the response
        if 'requirements' not in representation or representation['requirements'] is None:
            representation['requirements'] = []
        return representation


class ProgramImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramImage
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class MessageContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_read')


class UserCreateWithProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'type', 'gender', 'phone', 'date_of_birth')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'type': {'required': True},
            'gender': {'required': True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            type=validated_data.get('type', 'S'),  # Default to Student
            gender=validated_data.get('gender', 'O'),  # Default to Other
            phone=validated_data.get('phone', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            password=validated_data['password']
        )
        return user