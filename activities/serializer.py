from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer

class UserCreateWithProfileSerializer(UserCreateSerializer):
    """
    Extends Djoser's UserCreateSerializer to include profile image and additional fields.
    Used for user registration through Djoser.
    """
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'password', 'type', 'gender',
                  'bio', 'date_enrollment', 'phone', 'date_of_birth',
                  'first_name', 'last_name', 'profile_image']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the `User` model.
    This serializer includes all fields of the `User` model including the profile image.
    It is used to convert `User` model instances into JSON format and vice versa.
    """
    class Meta:
        model = User  # Specifies the model to be serialized
        fields = [
            'id', 'email', 'username', 'type', 'gender', 'bio', 
            'date_enrollment', 'phone', 'date_of_birth', 
            'first_name', 'last_name', 'profile_image',
        ]
        extra_kwargs = {
            'password': {'write_only': True}, # Hide password in the API responses
        }

class RequirementSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Requirement` model.
    This serializer includes all fields of the `Requirement` model.
    It is used to convert `Requirement` model instances into JSON format and vice versa.
    """
    class Meta:
        model = Requirement  # Specifies the model to be serialized
        fields = ['id', 'description'] # exclude the redundant inherited fields to reduce payload size

class ProgramImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the `ProgramImage` model.
    This serializer includes all fields of the `ProgramImage` model.
    It is used to convert `ProgramImage` model instances into JSON format and vice versa.
    """
    class Meta:
        model = ProgramImage
        fields = ['id', 'image', 'caption']

class ProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Program` model.
    This serializer includes all fields of the `Program` model and related requirements.
    It is used to convert `Program` model instances into JSON format and vice versa.
    """
    requirements = RequirementSerializer(many=True, read_only=True) # Nested serializer for the Requirement model
    additional_images = ProgramImageSerializer(many=True, read_only=True) # Nested serializer for additional images
    
    class Meta:
        model = Program  # Specifies the model to be serialized
        fields = [
            'id', 'title', 'description', 'cost', 'start_date', 
            'end_date', 'post_date', 'url', 'type', 'category', 
            'audience', 'kind', 'target_academic', 'requirements',
            'image', 'additional_images'
        ]
        
class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Favorite` model.
    This serializer includes all fields of the `Favorite` model.
    It is used to convert `Favorite` model instances into JSON format and vice versa.
    """
    program = serializers.CharField(source='program.title', read_only=True) # Display the title of the program

    class Meta:
        model = Favorite  # Specifies the model to be serialized
        fields = ['id', 'program']

class WeeklyEmailSerializer(serializers.ModelSerializer):
    """
    Serializer for the `WeeklyEmail` model.
    Fields:
    - `id`: Unique identifier for the weekly email.
    - `subject`: Subject of the weekly email.
    - `sent_date`: Date when the email was sent.
    - `users`: List of users who received the email (nested `UserSerializer`).
    - `programs`: List of programs included in the email (nested `ProgramSerializer`).
    """
    users = UserSerializer(many=True, read_only=True) # Nested users
    programs = ProgramSerializer(many=True, read_only=True) # Nested programs
    
    class Meta:
        model = WeeklyEmail
        fields = ['id', 'subject', 'sent_date', 'users', 'programs']

class EmailLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the `EmailLog` model.
    This serializer includes all fields of the `EmailLog` model.
    It is used to convert `EmailLog` model instances into JSON format and vice versa.
    """
    class Meta:
        model = EmailLog  # Specifies the model to be serialized
        fields = ['id', 'status', 'timestamp']

class MessageContactSerializer(serializers.ModelSerializer):
    """
    Serializer for the `MessageContact` model.
    This serializer includes all fields of the `MessageContact` model.
    It is used to convert `MessageContact` model instances into JSON format and vice versa.
    """
    class Meta:
        model = MessageContact  # Specifies the model to be serialized
        fields = [
            'id', 'name', 'email', 'phone', 'message', 
            'status', 'read_at', 'responded_at'
        ]