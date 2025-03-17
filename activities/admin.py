from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Program, Requirement, ProgramRequirement, Favorite, EmailLog, WeeklyEmail, WeeklyUserEmail, ProgramEmail, MessageContact


admin.site.register(User)
admin.site.register(Program)
admin.site.register(Requirement)
admin.site.register(ProgramRequirement)
admin.site.register(Favorite)
admin.site.register(EmailLog)
admin.site.register(WeeklyEmail)
admin.site.register(WeeklyUserEmail)
admin.site.register(ProgramEmail)
admin.site.register(MessageContact)
