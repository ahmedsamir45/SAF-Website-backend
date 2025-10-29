import os
import shutil
import logging
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
import uuid
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Set up logging
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Abstract Base Model
# -------------------------------------------------------------------
class BaseModel(models.Model):
    """Common abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


# -------------------------------------------------------------------
# Contact Message Model
# -------------------------------------------------------------------
class ContactMessage(BaseModel):
    """Stores contact messages from users."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"


# -------------------------------------------------------------------
# Enums
# -------------------------------------------------------------------
class UserType(models.TextChoices):
    STUDENT = 'S', 'Student'
    TEACHER = 'T', 'Teacher'
    ADMIN = 'A', 'Admin'


class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'


class ProgramType(models.TextChoices):
    ONLINE = 'ON', 'Online'
    OFFLINE = 'OFF', 'Offline'
    HYBRID = 'HY', 'Hybrid'


class ProgramCategory(models.TextChoices):
    TECHNOLOGY = 'TECH', 'Technology'
    BUSINESS = 'BUS', 'Business'
    ART = 'ART', 'Art'
    SCIENCE = 'SCI', 'Science'


class ProgramAudience(models.TextChoices):
    BEGINNER = 'BEG', 'Beginner'
    INTERMEDIATE = 'INT', 'Intermediate'
    ADVANCED = 'ADV', 'Advanced'


class ProgramKind(models.TextChoices):
    JOB = 'JOB', 'Job'
    INTERN = 'INTERN', 'Internship'
    SCHOLAR = 'SCHOLAR', 'Scholarship'


class TargetAcademic(models.TextChoices):
    STUDENT = 'STUDENT', 'Student'
    GRADUATE = 'GRADUATE', 'Graduate'
    BOTH = 'BOTH', 'Both'


class EmailStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    SENDING = 'sending', _('Sending')
    SENT = 'sent', _('Sent')
    FAILED = 'failed', _('Failed')
    PARTIALLY_SENT = 'partially_sent', _('Partially Sent')


# -------------------------------------------------------------------
# Category & Blog Models
# -------------------------------------------------------------------
class Category(BaseModel):
    """Represents a blog category."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(BaseModel):
    """Represents a blog post."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='published_at')
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='blog_posts')
    categories = models.ManyToManyField(Category, related_name='blog_posts', blank=True)
    featured_image = models.ImageField(
        upload_to='blog/images/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-published_at']
        get_latest_by = 'published_at'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        if not self.excerpt:
            self.excerpt = (self.content[:500] + '...') if len(self.content) > 500 else self.content
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


# -------------------------------------------------------------------
# Newsletter Subscription
# -------------------------------------------------------------------
class NewsletterSubscription(BaseModel):
    """Newsletter subscriber with email verification."""
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=False)  # Inactive until email is verified
    activation_code = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    activation_sent_at = models.DateTimeField(null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['activation_code']),
        ]

    def __str__(self):
        return self.email
        
    def unsubscribe(self):
        """Mark the subscription as unsubscribed."""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])


# -------------------------------------------------------------------
# Upload paths
# -------------------------------------------------------------------
def user_profile_image_path(instance, filename):
    return f'user_profiles/{instance.id}/{filename}'


def program_image_path(instance, filename):
    """
    Return the path for program images.
    If the instance doesn't have an ID yet (new instance), use a temporary path.
    """
    # Get file extension
    ext = filename.split('.')[-1]
    # Create a unique filename using UUID
    unique_filename = f"{uuid.uuid4()}.{ext}"
    
    if not instance.pk:  # If the instance hasn't been saved yet
        # Use a temporary directory with a timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        return f'program_images/temp/{timestamp}_{unique_filename}'
    return f'program_images/program_{instance.id}/{unique_filename}'

# -------------------------------------------------------------------
# Custom User Manager
# -------------------------------------------------------------------
class UserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifier for authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
            
        return self.create_user(email, password, **extra_fields)


# -------------------------------------------------------------------
# User Model
# -------------------------------------------------------------------
class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    type = models.CharField(max_length=1, choices=UserType.choices, default=UserType.STUDENT)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.OTHER)
    bio = models.TextField(blank=True, null=True)
    date_enrollment = models.DateField(default=now)
    phone = PhoneNumberField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to=user_profile_image_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    is_verified = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='saf_user_groups',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='saf_user_permissions',
        related_query_name='user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# -------------------------------------------------------------------
# Program Models
# -------------------------------------------------------------------
class Requirement(BaseModel):
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description


class Program(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    post_date = models.DateField(default=now)
    url = models.URLField()
    type = models.CharField(max_length=50, choices=ProgramType.choices, default=ProgramType.ONLINE)
    category = models.CharField(max_length=50, choices=ProgramCategory.choices, default=ProgramCategory.TECHNOLOGY)
    audience = models.CharField(max_length=50, choices=ProgramAudience.choices, default=ProgramAudience.BEGINNER)
    kind = models.CharField(max_length=50, choices=ProgramKind.choices, default=ProgramKind.JOB)
    target_academic = models.CharField(max_length=50, choices=TargetAcademic.choices, default=TargetAcademic.BOTH)
    requirements = models.ManyToManyField(Requirement, through='ProgramRequirement', related_name='programs')
    image = models.ImageField(upload_to=program_image_path, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    _old_image = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._old_image = self.image

    def save(self, *args, **kwargs):
        # Check if this is a new instance or if the image has changed
        is_new = not self.pk
        image_changed = not is_new and self._old_image != self.image
        
        # Save the instance first to get an ID
        super().save(*args, **kwargs)
        
        # If this is an existing instance and the image has changed, delete the old image
        if not is_new and image_changed and self._old_image:
            self._delete_file(self._old_image)
        
        # If there's an image in the temp directory, move it to the final location
        if self.image and 'temp' in self.image.name:
            self._move_temp_file()
    
    def delete(self, *args, **kwargs):
        """Delete the model instance and its associated files."""
        # Delete the image file before deleting the model
        if self.image:
            self._delete_file(self.image)
        super().delete(*args, **kwargs)
    
    def _move_temp_file(self):
        """Move a file from the temp directory to its final location."""
        if not self.image or not self.pk:
            return
            
        old_path = self.image.path
        filename = os.path.basename(self.image.name)
        new_relative_path = f'program_images/program_{self.id}/{filename}'
        new_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)
        
        try:
            # Create the target directory if it doesn't exist
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # Move the file
            shutil.move(old_path, new_path)
            
            # Update the image field
            self.image.name = new_relative_path
            # Use update_fields to prevent recursive save
            Program.objects.filter(pk=self.pk).update(image=new_relative_path)
            
            # Remove the old directory if it's empty
            try:
                os.rmdir(os.path.dirname(old_path))
            except OSError:
                pass  # Directory not empty or already deleted
                
        except Exception as e:
            print(f"Error moving file: {e}")
    
    def _delete_file(self, file_field):
        """Delete the file if it exists."""
        if file_field and hasattr(file_field, 'storage') and hasattr(file_field, 'path'):
            try:
                file_path = file_field.path
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    # Try to remove the directory if it's empty
                    try:
                        os.rmdir(os.path.dirname(file_path))
                    except OSError:
                        pass  # Directory not empty or already deleted
            except Exception as e:
                print(f"Error deleting file: {e}")

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(start_date__lte=models.F('end_date')), name='start_date_lte_end_date')
        ]

    def __str__(self):
        return self.title


class ProgramRequirement(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.program.title} - {self.requirement.description}"


class ProgramImage(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to=program_image_path)
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.program.title}"


class Favorite(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='favorites')

    def __str__(self):
        return f"{self.user.email} - {self.program.title}"


# -------------------------------------------------------------------
# Email Tracking Models
# -------------------------------------------------------------------
class EmailLog(BaseModel):
    status = models.CharField(max_length=50, choices=EmailStatus.choices, default=EmailStatus.PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmailLog {self.id} - {self.status}"



class WeeklyEmail(BaseModel):
    subject = models.CharField(
        max_length=255,
        default="Newsletter Update"
    )
    content = models.TextField(
        help_text="HTML content for the email",
        default="<p>Thank you for subscribing to our newsletter!</p>"
    )
    
    # Single datetime field for scheduling
    scheduled_for = models.DateTimeField(
        help_text="The date and time when the email should be sent",
        default=timezone.now
    )
    
    subscribers = models.ManyToManyField(
        'NewsletterSubscription',
        related_name='emails_received',
        blank=True,
        help_text="Subscribers who should receive this email"
    )
    programs = models.ManyToManyField(
        Program,
        related_name='weekly_emails',
        blank=True,
        help_text="Programs to feature in this email"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.PENDING
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, null=True)
    success_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    
    # For backward compatibility
    @property
    def email_sent(self):
        return self.status in [EmailStatus.SENT, EmailStatus.PARTIALLY_SENT]
    
    @property
    def scheduled_date(self):
        return self.scheduled_for.date() if self.scheduled_for else None
    
    @property
    def scheduled_hour(self):
        return self.scheduled_for.hour if self.scheduled_for else 12
    
    @property
    def scheduled_minute(self):
        return self.scheduled_for.minute if self.scheduled_for else 0
    
    @property
    def scheduled_second(self):
        return self.scheduled_for.second if self.scheduled_for else 0

    class Meta:
        verbose_name = 'Scheduled Email'
        verbose_name_plural = 'Scheduled Emails'
        ordering = ['-scheduled_for']

    @property
    def status_display(self):
        """Return the human-readable status."""
        if not self.status:
            return ""
        return dict(EmailStatus.choices).get(self.status, self.status)

    def __str__(self):
        status = "Sent" if self.email_sent else f"Scheduled for {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"
        return f"{self.subject} - {status}"
    
    def save(self, *args, **kwargs):
        # Only prevent modifications to fully sent emails
        if self.pk and self.status == EmailStatus.SENT:
            return self
        return super().save(*args, **kwargs)
    
    def get_subscribers(self):
        """Get all active newsletter subscribers"""
        return NewsletterSubscription.objects.filter(is_active=True)
    
    def get_scheduled_datetime(self):
        """
        Return the full scheduled datetime by combining date, hour, minute, and second.
        """
        from django.utils import timezone
        from datetime import datetime, time as dt_time
        
        # Create a timezone-aware datetime from the components
        scheduled_time = dt_time(
            hour=self.scheduled_hour,
            minute=self.scheduled_minute,
            second=self.scheduled_second
        )
        return timezone.make_aware(
            datetime.combine(self.scheduled_date, scheduled_time)
        )
    
    def is_ready_to_send(self):
        """Check if it's time to send this email"""
        if self.email_sent:
            return False
            
        now = timezone.now()
        scheduled_time = self.get_scheduled_datetime()
        return now >= scheduled_time
    
    def send_emails(self, max_retries=3):
        """
        Send this email to all active newsletter subscribers with retry logic.
        Returns True if all emails were sent successfully, False otherwise.
        """
        from django.core.mail import EmailMultiAlternatives, BadHeaderError
        from django.template.loader import render_to_string, TemplateDoesNotExist
        from django.conf import settings
        from django.utils import timezone
        from smtplib import SMTPException, SMTPResponseException
        from socket import error as SocketError
        from email.utils import formataddr
        import time
        from django.db import transaction, connection
        
        # Don't send if already sent or currently sending
        if self.status in [EmailStatus.SENT, EmailStatus.SENDING]:
            logger.warning(f"Email {self.id} already in state: {self.status}")
            return False
            
        # Get active subscribers
        subscribers = self.get_subscribers()
        total_subscribers = subscribers.count()
        
        if not total_subscribers:
            logger.warning("No active subscribers to send the newsletter to.")
            return False
            
        logger.info(f"Starting to send email {self.id} to {total_subscribers} subscribers")
        
        # Update status to sending with retry logic
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                with transaction.atomic():
                    self.refresh_from_db()
                    if self.status in [EmailStatus.SENT, EmailStatus.SENDING]:
                        logger.warning(f"Email {self.id} already in state: {self.status}")
                        return False
                    self.status = EmailStatus.SENDING
                    self.save(update_fields=['status', 'updated_at'])
                    break  # Success, exit retry loop
            except Exception as e:
                if attempt == max_attempts - 1:  # Last attempt
                    logger.error(f"Failed to update status to SENDING after {max_attempts} attempts: {str(e)}")
                    return False
                time.sleep(1)  # Wait before retrying
        
        success_count = 0
        failure_count = 0
        
        # Get base URL with fallback
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        from_email = formataddr((
            getattr(settings, 'DEFAULT_FROM_NAME', 'SAF Newsletter'),
            settings.DEFAULT_FROM_EMAIL
        ))
        
        # Process subscribers in chunks to prevent memory issues
        subscriber_chunks = [subscribers[i:i + 10] for i in range(0, len(subscribers), 10)]
        
        for chunk in subscriber_chunks:
            for subscriber in chunk:
                retry_count = 0
                sent = False
                last_error = None
                
                while retry_count <= max_retries and not sent:
                    try:
                        # Prepare email context
                        context = {
                            'email': self,
                            'subscriber': subscriber,
                            'site_url': base_url,
                            'unsubscribe_url': f"{base_url}/api/newsletter-subscriptions/{subscriber.email}/unsubscribe/"
                        }
                        
                        # Render email content with better error handling
                        try:
                            html_content = render_to_string('emails/newsletter_template.html', context)
                        except TemplateDoesNotExist:
                            logger.warning("Custom template not found, using default content")
                            html_content = f"<div>{self.content}</div>"
                        except Exception as e:
                            logger.error(f"Template rendering error: {str(e)}", exc_info=True)
                            html_content = f"<div>{self.content}</div>"
                        
                        text_content = "Please enable HTML to view this email."
                        
                        # Create and send email
                        try:
                            msg = EmailMultiAlternatives(
                                subject=self.subject,
                                body=text_content,
                                from_email=from_email,
                                to=[subscriber.email],
                                reply_to=[from_email],
                                headers={
                                    'X-Auto-Response-Suppress': 'OOF, AutoReply',
                                    'Precedence': 'bulk',
                                    'X-SAF-Email-ID': str(self.id),
                                    'List-Unsubscribe': f'<mailto:{from_email}?subject=Unsubscribe>',
                                    'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
                                }
                            )
                            msg.attach_alternative(html_content, "text/html")
                            
                            # Send the email
                            msg.send(fail_silently=False)
                            
                            # Record successful send with retry logic
                            sub_success = False
                            for sub_attempt in range(3):
                                try:
                                    with transaction.atomic():
                                        self.subscribers.add(subscriber)
                                        success_count += 1
                                        sub_success = True
                                        sent = True
                                        logger.info(f"Successfully sent to {subscriber.email}")
                                        break  # Success, exit retry loop
                                except Exception as e:
                                    if sub_attempt == 2:  # Last attempt
                                        logger.error(f"Failed to update subscriber {subscriber.email}: {str(e)}")
                                        # Continue with next subscriber even if DB update fails
                                        sent = True  # Mark as sent to avoid retry loop
                                        success_count += 1
                                    time.sleep(0.5)  # Short delay before retry
                            
                        except (BadHeaderError, SMTPException, SMTPResponseException, SocketError) as e:
                            last_error = str(e)
                            retry_count += 1
                            
                            if retry_count <= max_retries:
                                # Exponential backoff
                                wait_time = min(2 ** retry_count, 30)  # Cap at 30 seconds
                                logger.warning(
                                    f"Attempt {retry_count} failed for {subscriber.email}. "
                                    f"Retrying in {wait_time} seconds. Error: {last_error}"
                                )
                                time.sleep(wait_time)
                        except Exception as e:
                            logger.error(f"Failed to update subscriber {subscriber.email}: {str(e)}")
                            # Continue with next subscriber even if DB update fails
                            sent = True  # Mark as sent to avoid retry loop
                            success_count += 1

                    except (BadHeaderError, SMTPException, SMTPResponseException, SocketError) as e:
                        last_error = str(e)
                        retry_count += 1

                        if retry_count <= max_retries:
                            # Exponential backoff
                            wait_time = min(2 ** retry_count, 30)  # Cap at 30 seconds
                            logger.warning(
                                f"Attempt {retry_count} failed for {subscriber.email}. "
                                f"Retrying in {wait_time} seconds. Error: {last_error}"
                            )
                            time.sleep(wait_time)
                        else:
                            failure_count += 1
                            self.last_error = f"{subscriber.email}: {last_error}"
                            logger.error(
                                f"Failed to send to {subscriber.email} after {max_retries} attempts. "
                                f"Error: {last_error}",
                                exc_info=True
                            )

                    except Exception as e:
                        last_error = str(e)
                        failure_count += 1
                        self.last_error = f"{subscriber.email}: {last_error}"
                        logger.error(
                            f"Unexpected error sending to {subscriber.email}: {last_error}",
                            exc_info=True
                        )
                        break  # Don't retry on unexpected errors
                
        # Update email status and statistics with retry logic
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                with transaction.atomic():
                    # Refresh the object to avoid StaleDataError
                    self.refresh_from_db()
                    
                    if failure_count == 0:
                        self.status = EmailStatus.SENT
                        self.sent_at = timezone.now()
                    elif success_count > 0:
                        self.status = EmailStatus.PARTIALLY_SENT
                    else:
                        self.status = EmailStatus.FAILED
                    
                    self.success_count = success_count
                    self.failure_count = failure_count
                    
                    update_fields = [
                        'status', 'sent_at', 'last_error', 
                        'success_count', 'failure_count', 'updated_at'
                    ]
                    
                    self.save(update_fields=update_fields)
                    
                    # Log the result
                    if failure_count == 0:
                        logger.info(
                            f"Successfully sent email {self.id} to all {success_count} subscribers"
                        )
                    else:
                        logger.warning(
                            f"Email {self.id} sending completed with {success_count} successes "
                            f"and {failure_count} failures"
                        )
                    
                    return failure_count == 0
                    
            except Exception as e:
                if attempt == max_attempts - 1:  # Last attempt
                    logger.error(f"Failed to update email status after {max_attempts} attempts: {str(e)}")
                    return False
                time.sleep(1)  # Wait before retrying
        
        return failure_count == 0
