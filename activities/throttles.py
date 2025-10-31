from rest_framework.throttling import AnonRateThrottle
from django.conf import settings

class NewsletterSubscriptionThrottle(AnonRateThrottle):
    """
    Throttle for newsletter subscription endpoints to prevent abuse.
    Limits:
    - 5 requests per hour for anonymous users in production
    - 100 requests per hour for development
    """
    scope = 'subscription'
    
    def get_rate(self):
        # More permissive rate in development
        if settings.DEBUG:
            return '100/hour'
        return '5/hour'

class NewsletterConfirmThrottle(AnonRateThrottle):
    """
    Throttle for newsletter confirmation endpoint.
    Limits:
    - 10 requests per hour for anonymous users in production
    - 100 requests per hour for development
    """
    scope = 'confirm_subscription'
    
    def get_rate(self):
        # More permissive rate in development
        if settings.DEBUG:
            return '100/hour'
        return '10/hour'
