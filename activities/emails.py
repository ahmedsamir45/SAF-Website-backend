from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from .models import EmailLog, WeeklyEmail, NewsletterSubscription
import logging

logger = logging.getLogger(__name__)

def send_weekly_newsletter():
    """
    Sends the weekly newsletter to all active subscribers.
    This is a legacy function - new code should use the WeeklyEmail.send_emails() method.
    """
    try:
        # Get the most recent unsent weekly email
        weekly_email = WeeklyEmail.objects.filter(
            scheduled_for__lte=timezone.now(),
            status=EmailStatus.PENDING
        ).order_by('scheduled_for').first()

        if not weekly_email:
            logger.info("No pending weekly emails to send.")
            return

        # Use the model's send_emails method which has better error handling
        success = weekly_email.send_emails()
        
        if success:
            logger.info(
                f"Successfully sent weekly newsletter to {weekly_email.success_count} "
                f"subscribers (failures: {weekly_email.failure_count})."
            )
        else:
            logger.error(
                f"Failed to send weekly newsletter. "
                f"Success: {weekly_email.success_count}, "
                f"Failures: {weekly_email.failure_count}, "
                f"Error: {weekly_email.last_error}"
            )

    except Exception as e:
        logger.error(f"Error in send_weekly_newsletter: {str(e)}", exc_info=True)
        raise
