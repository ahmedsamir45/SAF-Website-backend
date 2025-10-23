import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SAF_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

# Test user credentials
TEST_EMAIL = 'test@example.com'
TEST_USERNAME = 'test@example.com'

def check_user():
    """Check if test user exists and their status"""
    User = get_user_model()
    
    try:
        # Check if user exists
        user = User.objects.get(username=TEST_USERNAME)
        print("\n=== User Found ===")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Active: {user.is_active}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print(f"Last Login: {user.last_login}")
        print(f"Date Joined: {user.date_joined}")
        
        # Check if password is set
        if user.check_password('testpass123'):
            print("✅ Password is correct")
        else:
            print("❌ Password is incorrect")
            
        # Check authentication
        from django.contrib.auth import authenticate
        auth_user = authenticate(username=TEST_USERNAME, password='testpass123')
        if auth_user:
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            
    except User.DoesNotExist:
        print(f"❌ User with username '{TEST_USERNAME}' does not exist")
    
    # Print database tables for debugging
    print("\n=== Database Tables ===")
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        print("\n".join([table[0] for table in tables]))

if __name__ == "__main__":
    check_user()
