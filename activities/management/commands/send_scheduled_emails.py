from django.core.management.base import BaseCommand
from django.utils import timezone
from activities.models import WeeklyEmail, EmailStatus
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends scheduled emails that are due'

    def handle(self, *args, **options):
        """
        Check for and send any scheduled emails that are due to be sent.
        This should be run periodically (e.g., every minute via cron or Celery beat).
        """
        self.stdout.write("Checking for scheduled emails to send...")
        
        # Get all pending emails that are scheduled to be sent now or in the past
        now = timezone.now()
        emails_to_send = WeeklyEmail.objects.filter(
            status=EmailStatus.PENDING,
            scheduled_for__lte=now
        ).order_by('scheduled_for')
        
        self.stdout.write(f"Found {emails_to_send.count()} emails to process")
        
        sent_count = 0
        failed_count = 0
        
        for email in emails_to_send:
            self.stdout.write(f"Processing email: {email.subject} (ID: {email.id})")
            try:
                if email.send_emails():
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully sent email '{email.subject}' to "
                            f"{email.success_count} recipients"
                        )
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Email '{email.subject}' completed with {email.failure_count} "
                            f"failures. Status: {email.get_status_display()}"
                        )
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending email {email.id}: {str(e)}", exc_info=True)
                self.stdout.write(
                    self.style.ERROR(
                        f"Error sending email {email.id} ({email.subject}): {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Processing complete. Sent: {sent_count}, Failed: {failed_count}"
            )
        )
