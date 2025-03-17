from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

# Abstract Base Models
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Enums for choices
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

class MessageStatus(models.TextChoices):
    NEW = 'NEW', 'New'
    READ = 'READ', 'Read'
    RESPONDED = 'RESPONDED', 'Responded'

# Models
class User(AbstractUser, BaseModel):
    type = models.CharField(max_length=1, choices=UserType.choices, default=UserType.STUDENT)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.OTHER)
    bio = models.TextField(blank=True, null=True)
    date_enrollment = models.DateField(default=now)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, type={self.type})"

    def __str__(self):
        return self.username

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

    def __repr__(self):
        return f"Program(id={self.id}, title={self.title}, kind={self.kind})"

    def __str__(self):
        return self.title

class Requirement(BaseModel):
    description = models.CharField(max_length=255)

    def __repr__(self):
        return f"Requirement(id={self.id}, description={self.description})"

    def __str__(self):
        return self.description

class ProgramRequirement(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)

    def __repr__(self):
        return f"ProgramRequirement(id={self.id}, program={self.program.title}, requirement={self.requirement.description})"

    def __str__(self):
        return f"{self.program.title} - {self.requirement.description}"

class Favorite(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    def __repr__(self):
        return f"Favorite(id={self.id}, user={self.user.username}, program={self.program.title})"

    def __str__(self):
        return f"{self.user.username} - {self.program.title}"

class EmailLog(BaseModel):
    status = models.CharField(max_length=50, choices=EmailStatus.choices, default=EmailStatus.PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"EmailLog(id={self.id}, status={self.status}, timestamp={self.timestamp})"

    def __str__(self):
        return f"EmailLog {self.id} - {self.status}"

class WeeklyEmail(BaseModel):
    subject = models.CharField(max_length=255)
    sent_date = models.DateField(default=now)

    def __repr__(self):
        return f"WeeklyEmail(id={self.id}, subject={self.subject}, sent_date={self.sent_date})"

    def __str__(self):
        return self.subject

class WeeklyUserEmail(BaseModel):
    email = models.ForeignKey(WeeklyEmail, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __repr__(self):
        return f"WeeklyUserEmail(id={self.id}, email={self.email.subject}, user={self.user.username})"

    def __str__(self):
        return f"{self.email.subject} - {self.user.username}"

class ProgramEmail(BaseModel):
    email = models.ForeignKey(WeeklyEmail, on_delete=models.CASCADE)  # Fixed relationship
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    def __repr__(self):
        return f"ProgramEmail(id={self.id}, email={self.email.subject}, program={self.program.title})"

    def __str__(self):
        return f"{self.email.subject} - {self.program.title}"

class MessageContact(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=MessageStatus.choices, default=MessageStatus.NEW)

    def __repr__(self):
        return f"MessageContact(id={self.id}, name={self.name}, status={self.status})"

    def __str__(self):
        return f"{self.name} - {self.status}"