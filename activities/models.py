from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField

# Abstract Base Models
class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models.
    - `created_at`: Automatically set to the current date and time when the object is created.
    - `updated_at`: Automatically updated to the current date and time whenever the object is saved.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This makes BaseModel an abstract class, so it won't create a database table.

# Enums for choices
class UserType(models.TextChoices):
    """
    Enum for user types.
    - STUDENT: Represents a student user.
    - TEACHER: Represents a teacher user.
    - ADMIN: Represents an admin user.
    """
    STUDENT = 'S', 'Student'
    TEACHER = 'T', 'Teacher'
    ADMIN = 'A', 'Admin'

class Gender(models.TextChoices):
    """
    Enum for gender choices.
    - MALE: Represents male gender.
    - FEMALE: Represents female gender.
    - OTHER: Represents other gender.
    """
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'

class ProgramType(models.TextChoices):
    """
    Enum for program types.
    - ONLINE: Represents an online program.
    - OFFLINE: Represents an offline program.
    - HYBRID: Represents a hybrid program (both online and offline).
    """
    ONLINE = 'ON', 'Online'
    OFFLINE = 'OFF', 'Offline'
    HYBRID = 'HY', 'Hybrid'

class ProgramCategory(models.TextChoices):
    """
    Enum for program categories.
    - TECHNOLOGY: Represents technology-related programs.
    - BUSINESS: Represents business-related programs.
    - ART: Represents art-related programs.
    - SCIENCE: Represents science-related programs.
    """
    TECHNOLOGY = 'TECH', 'Technology'
    BUSINESS = 'BUS', 'Business'
    ART = 'ART', 'Art'
    SCIENCE = 'SCI', 'Science'

class ProgramAudience(models.TextChoices):
    """
    Enum for program audience levels.
    - BEGINNER: Represents programs for beginners.
    - INTERMEDIATE: Represents programs for intermediate users.
    - ADVANCED: Represents programs for advanced users.
    """
    BEGINNER = 'BEG', 'Beginner'
    INTERMEDIATE = 'INT', 'Intermediate'
    ADVANCED = 'ADV', 'Advanced'

class ProgramKind(models.TextChoices):
    """
    Enum for program kinds.
    - JOB: Represents job-related programs.
    - INTERN: Represents internship programs.
    - SCHOLAR: Represents scholarship programs.
    """
    JOB = 'JOB', 'Job'
    INTERN = 'INTERN', 'Internship'
    SCHOLAR = 'SCHOLAR', 'Scholarship'

class TargetAcademic(models.TextChoices):
    """
    Enum for target academic levels.
    - STUDENT: Represents programs targeted at students.
    - GRADUATE: Represents programs targeted at graduates.
    - BOTH: Represents programs targeted at both students and graduates.
    """
    STUDENT = 'STUDENT', 'Student'
    GRADUATE = 'GRADUATE', 'Graduate'
    BOTH = 'BOTH', 'Both'

class EmailStatus(models.TextChoices):
    """
    Enum for email statuses.
    - SENT: Represents emails that have been sent.
    - FAILED: Represents emails that failed to send.
    - PENDING: Represents emails that are pending to be sent.
    """
    SENT = 'SENT', 'Sent'
    FAILED = 'FAILED', 'Failed'
    PENDING = 'PENDING', 'Pending'

class MessageStatus(models.TextChoices):
    """
    Enum for message statuses.
    - NEW: Represents new messages.
    - READ: Represents messages that have been read.
    - RESPONDED: Represents messages that have been responded to.
    """
    NEW = 'NEW', 'New'
    READ = 'READ', 'Read'
    RESPONDED = 'RESPONDED', 'Responded'

# Function to define upload paths
def user_profile_image_path(instance, filename):
    """
    Function to define the upload path for user profile images.
    Format: 'user_profiles/user_id/filename'
    """
    return f'user_profiles/{instance.id}/{filename}'

def program_image_path(instance, filename):
    """
    Function to define the upload path for program images.
    Format: 'program_images/program_id/filename'
    """
    return f'program_images/{instance.id}/{filename}'

# Models
class User(AbstractUser, BaseModel):
    """
    Custom user model that extends Django's AbstractUser and BaseModel.
    - `type`: The type of user (Student, Teacher, Admin).
    - `gender`: The gender of the user.
    - `bio`: A short biography of the user.
    - `date_enrollment`: The date the user enrolled.
    - `phone`: The user's phone number.
    - `date_of_birth`: The user's date of birth.
    - `profile_image`: The user's profile image.
    """
    type = models.CharField(max_length=1, choices=UserType.choices, default=UserType.STUDENT, db_index=True) # db_index for faster filtering
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.OTHER, db_index=True)
    bio = models.TextField(blank=True, null=True)
    date_enrollment = models.DateField(default=now, db_index=True)
    phone = PhoneNumberField(blank=True, null=True) # better phone number validation
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to=user_profile_image_path, blank=True, null=True)

    def __repr__(self):
        """Returns a detailed string representation of the User object."""
        return f"User(id={self.id}, username={self.username}, type={self.type})"

    def __str__(self):
        """Returns a simple string representation of the User object."""
        return self.username



class Requirement(BaseModel):
    """
    Model representing a requirement for a program.
    - `description`: A description of the requirement.
    """
    description = models.CharField(max_length=255)

    def __repr__(self):
        """Returns a detailed string representation of the Requirement object."""
        return f"Requirement(id={self.id}, description={self.description})"

    def __str__(self):
        """Returns a simple string representation of the Requirement object."""
        return self.description
# Then define ProgramRequirement
class ProgramRequirement(BaseModel):
    program = models.ForeignKey('Program', on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.program.title} - {self.requirement.description}"
class Program(BaseModel):
    """
    Model representing a program.
    - `title`: The title of the program.
    - `description`: A detailed description of the program.
    - `cost`: The cost of the program.
    - `start_date`: The start date of the program.
    - `end_date`: The end date of the program.
    - `post_date`: The date the program was posted.
    - `url`: The URL for more information about the program.
    - `type`: The type of program (Online, Offline, Hybrid).
    - `category`: The category of the program (Technology, Business, Art, Science).
    - `audience`: The target audience level (Beginner, Intermediate, Advanced).
    - `kind`: The kind of program (Job, Internship, Scholarship).
    - `target_academic`: The target academic level (Student, Graduate, Both).
    - `image`: The program's featured image.
    """
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    post_date = models.DateField(default=now)
    url = models.URLField()
    type = models.CharField(max_length=50, choices=ProgramType.choices, default=ProgramType.ONLINE, db_index=True)
    category = models.CharField(max_length=50, choices=ProgramCategory.choices, default=ProgramCategory.TECHNOLOGY, db_index=True)
    audience = models.CharField(max_length=50, choices=ProgramAudience.choices, default=ProgramAudience.BEGINNER, db_index=True)
    kind = models.CharField(max_length=50, choices=ProgramKind.choices, default=ProgramKind.JOB)
    target_academic = models.CharField(max_length=50, choices=TargetAcademic.choices, default=TargetAcademic.BOTH)
    requirements = models.ManyToManyField(Requirement, through='ProgramRequirement', related_name='programs')
    image = models.ImageField(upload_to=program_image_path, blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(start_date__lte=models.F('end_date')), name='start_date_lte_end_date') # check comstraint for start_date <= end_date
        ]

    def __repr__(self):
        """Returns a detailed string representation of the Program object."""
        return f"Program(id={self.id}, title={self.title}, kind={self.kind})"

    def __str__(self):
        """Returns a simple string representation of the Program object."""
        return self.title

class ProgramImage(BaseModel):
    """
    Model representing additional images for a program.
    - `program`: The program that the image belongs to.
    - `image`: The additional image for the program.
    - `caption`: An optional caption for the image.
    """
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to=program_image_path)
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __repr__(self):
        """Returns a detailed string representation of the ProgramImage object."""
        return f"ProgramImage(id={self.id}, program={self.program.title})"

    def __str__(self):
        """Returns a simple string representation of the ProgramImage object."""
        return f"Image for {self.program.title}"



class Favorite(BaseModel):
    """
    Model representing a user's favorite program.
    - `user`: The user who favorited the program.
    - `program`: The program that was favorited.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites') #  related_name allows reverse queries like user.favourites.all()
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='favorites')

    def __repr__(self):
        """Returns a detailed string representation of the Favorite object."""
        return f"Favorite(id={self.id}, user={self.user.username}, program={self.program.title})"

    def __str__(self):
        """Returns a simple string representation of the Favorite object."""
        return f"{self.user.username} - {self.program.title}"

class EmailLog(BaseModel):
    """
    Model representing an email log.
    - `status`: The status of the email (Sent, Failed, Pending).
    - `timestamp`: The timestamp when the email was logged.
    """
    status = models.CharField(max_length=50, choices=EmailStatus.choices, default=EmailStatus.PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        """Returns a detailed string representation of the EmailLog object."""
        return f"EmailLog(id={self.id}, status={self.status}, timestamp={self.timestamp})"

    def __str__(self):
        """Returns a simple string representation of the EmailLog object."""
        return f"EmailLog {self.id} - {self.status}"

class WeeklyEmail(BaseModel):
    """
    Model representing a weekly email.
    - `subject`: The subject of the email.
    - `sent_date`: The date the email was sent.
    """
    subject = models.CharField(max_length=255)
    sent_date = models.DateField(default=now, db_index=True)
    # simplifies the relationship between emails, users and programs
    users = models.ManyToManyField(User, related_name='weekly_emails') 
    programs = models.ManyToManyField(Program, related_name='weekly_emails')

    def __repr__(self):
        """Returns a detailed string representation of the WeeklyEmail object."""
        return f"WeeklyEmail(id={self.id}, subject={self.subject}, sent_date={self.sent_date})"

    def __str__(self):
        """Returns a simple string representation of the WeeklyEmail object."""
        return self.subject

class MessageContact(BaseModel):

    """
    Model representing a contact message.
    - `name`: The name of the person sending the message.
    - `email`: The email of the person sending the message.
    - `phone`: The phone number of the person sending the message.
    - `message`: The content of the message.
    - `status`: The status of the message (New, Read, Responded).
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=MessageStatus.choices, default=MessageStatus.NEW, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    def __repr__(self):
        """Returns a detailed string representation of the MessageContact object."""
        return f"MessageContact(id={self.id}, name={self.name}, status={self.status})"

    def __str__(self):
        """Returns a simple string representation of the MessageContact object."""
        return f"{self.name} - {self.status}"
    

# Add this model
