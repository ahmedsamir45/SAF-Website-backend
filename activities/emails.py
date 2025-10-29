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
    """
    try:
        # Get the most recent unsent weekly email
        weekly_email = WeeklyEmail.objects.filter(
            sent_date__lte=timezone.now().date(),
            email_sent=False
        ).first()

        if not weekly_email:
            logger.info("No pending weekly emails to send.")
            return

        # Get all active subscribers
        subscribers = NewsletterSubscription.objects.filter(is_active=True)
        
        if not subscribers.exists():
            logger.warning("No active subscribers found for the weekly newsletter.")
            return

        # Prepare common context for all emails
        base_context = {
            'programs': weekly_email.programs.all(),
            'site_url': settings.BASE_URL,
            'contact_email': settings.DEFAULT_FROM_EMAIL,
            'unsubscribe_url': f"{settings.BASE_URL}/unsubscribe/"
        }

        # Send email to each subscriber
        for subscriber in subscribers:
            try:
                context = {
                    **base_context,
                    'subscriber': subscriber,
                    'unsubscribe_url': f"{settings.BASE_URL}/unsubscribe/{subscriber.unsubscribe_token}/"
                }

                # Render email content
                html_content = render_to_string('emails/weekly_newsletter.html', context)
                text_content = "Please enable HTML emails to view this content."

                # Create and send email
                msg = EmailMultiAlternatives(
                    subject=weekly_email.subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email],
                    reply_to=[settings.DEFAULT_FROM_EMAIL]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # Log the email
                EmailLog.objects.create(
                    email_type='weekly_newsletter',
                    recipient=subscriber.email,
                    subject=weekly_email.subject,
                    status='sent'
                )

            except Exception as e:
                logger.error(f"Failed to send email to {subscriber.email}: {str(e)}")
                EmailLog.objects.create(
                    email_type='weekly_newsletter',
                    recipient=subscriber.email,
                    subject=weekly_email.subject,
                    status='failed',
                    error_message=str(e)
                )

        # Mark the weekly email as sent
        weekly_email.email_sent = True
        weekly_email.save()

        logger.info(f"Successfully sent weekly newsletter to {subscribers.count()} subscribers.")

    except Exception as e:
        logger.error(f"Error in send_weekly_newsletter: {str(e)}", exc_info=True)
