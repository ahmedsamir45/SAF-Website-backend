import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SAF_backend.settings')
django.setup()

def test_email():
    try:
        print("\n=== Testing Email Configuration ===")
        print(f"Sending test email from: {settings.DEFAULT_FROM_EMAIL}")
        print(f"Using SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        
        # Send a test email
        send_mail(
            'Test Email from Django',
            'This is a test email from your Django application.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Send to yourself
            fail_silently=False,
        )
        print("Test email sent successfully!")
        print("If you don't see the email, check your spam folder.")
        
    except Exception as e:
        print(f"\nError sending test email: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you've enabled 'Less secure app access' in your Google Account")
        print("   OR better, use an App Password if you have 2FA enabled")
        print("2. Check that your .env file has the correct SMTP settings")
        print("3. Verify that your firewall isn't blocking the SMTP port (587)")
        print("4. Try with a different email provider if possible")

if __name__ == "__main__":
    test_email()
