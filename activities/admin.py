from django.contrib import admin
from .models import (
    User, 
    Program, 
    Requirement, 
    Favorite, 
    EmailLog, 
    WeeklyEmail, 
    MessageContact,
    ProgramImage , # Add this if you want to manage program images in admin
    ProgramRequirement
)

# Register your models here
admin.site.register(User)
admin.site.register(Program)
admin.site.register(Requirement)
admin.site.register(Favorite)
admin.site.register(EmailLog)
admin.site.register(WeeklyEmail)
admin.site.register(MessageContact)
admin.site.register(ProgramImage)  # Add this if needed
admin.site.register(ProgramRequirement)