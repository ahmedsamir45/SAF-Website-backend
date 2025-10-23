import os
import shutil
from django.db import models
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
    SENT = 'SENT', 'Sent'
    FAILED = 'FAILED', 'Failed'
    PENDING = 'PENDING', 'Pending'


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
    """Newsletter subscriber."""
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=False)
    confirmation_code = models.UUIDField(default=uuid.uuid4, editable=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def confirm(self):
        self.is_active = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=['is_active', 'confirmed_at'])

    def unsubscribe(self):
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
    subject = models.CharField(max_length=255)
    sent_date = models.DateField(default=now)
    users = models.ManyToManyField(User, related_name='weekly_emails')
    programs = models.ManyToManyField(Program, related_name='weekly_emails')

    def __str__(self):
        return self.subject
