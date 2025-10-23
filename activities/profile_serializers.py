from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for detailed user profile with all fields"""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'type', 'gender', 
            'bio', 'date_enrollment', 'phone', 'date_of_birth', 'profile_image',
            'is_verified', 'email_notifications'
        ]
        read_only_fields = ['id', 'email', 'date_enrollment']