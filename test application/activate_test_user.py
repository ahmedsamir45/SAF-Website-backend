import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SAF_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

def activate_test_user():
    """Activate the test user and set a password"""
    User = get_user_model()
    
    try:
        user = User.objects.get(username='test@example.com')
        user.is_active = True
        user.save()
        print("✅ Test user activated successfully")
        print(f"Username: {user.username}")
        print(f"Is Active: {user.is_active}")
    except User.DoesNotExist:
        print("❌ Test user not found")
        # Create a new test user if it doesn't exist
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        print("✅ Created and activated new test user")

if __name__ == "__main__":
    activate_test_user()
