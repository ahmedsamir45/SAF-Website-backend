import os
import django
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SAF_backend.settings')
django.setup()

from django.core.mail import send_mail

def send_test_email():
    try:
        # Get email settings from environment
        from_email = os.getenv('DEFAULT_FROM_EMAIL')
        recipient_email = from_email  # Send to self by default
        
        if not from_email or '@' not in from_email:
            print("❌ Error: DEFAULT_FROM_EMAIL is not properly configured in .env file")
            return False
            
        subject = 'Test Email from SAF Backend'
        message = 'This is a test email to verify email service is working.'
        
        print("\n" + "="*50)
        print("Sending test email...")
        print(f"From: {from_email}")
        print(f"To: {recipient_email}")
        print(f"Subject: {subject}")
        print("="*50 + "\n")
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        print("✅ Test email sent successfully!")
        print(f"Please check the inbox of {recipient_email} for the test email.")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to send test email. Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your .env file for correct email settings")
        print("2. For Gmail, make sure you're using an App Password")
        print("3. Verify your internet connection")
        print("4. Check if your email provider allows SMTP access")
        return False

if __name__ == "__main__":
    print("=== SAF Backend Email Tester ===\n")
    
    # Check required settings
    required_settings = [
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'DEFAULT_FROM_EMAIL',
        'EMAIL_HOST',
        'EMAIL_PORT'
    ]
    
    missing_settings = [s for s in required_settings if not os.getenv(s)]
    
    if missing_settings:
        print("❌ Error: The following required settings are missing from .env:")
        for setting in missing_settings:
            print(f"- {setting}")
        print("\nPlease update your .env file with these settings and try again.")
    else:
        print("✓ All required email settings found in .env")
        print("\nSending test email...\n")
        send_test_email()
