from rest_framework.throttling import AnonRateThrottle

class NewsletterSubscriptionThrottle(AnonRateThrottle):
    """
    Throttle for newsletter subscription endpoints to prevent abuse.
    Limits:
    - 5 requests per hour for anonymous users
    """
    scope = 'subscription'
    rate = '5/hour'

class NewsletterConfirmThrottle(AnonRateThrottle):
    """
    Throttle for newsletter confirmation endpoint.
    Limits:
    - 10 requests per hour for anonymous users
    """
    scope = 'confirm_subscription'
    rate = '10/hour'
