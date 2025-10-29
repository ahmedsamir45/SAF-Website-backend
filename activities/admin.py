from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from django.db import models
from django.utils import timezone
from .models import (
    User, 
    Program, 
    Requirement, 
    Favorite, 
    EmailLog, 
    WeeklyEmail, 
    ContactMessage,
    ProgramImage,
    ProgramRequirement,
    Category,
    BlogPost,
    NewsletterSubscription
)

# Inline Admin Classes
class ProgramRequirementInline(admin.TabularInline):
    model = ProgramRequirement
    extra = 1
    verbose_name_plural = 'Program Requirements'
    autocomplete_fields = ['requirement']
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextInputWidget},
    }
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Make sure the formset has the proper prefix
        formset.form.base_fields['requirement'].widget.can_add_related = True
        formset.form.base_fields['requirement'].widget.can_change_related = True
        formset.form.base_fields['requirement'].widget.can_delete_related = True
        formset.form.base_fields['requirement'].widget.can_view_related = True
        return formset

class ProgramImageInline(admin.TabularInline):
    model = ProgramImage
    extra = 1
    fields = ('image', 'caption', 'image_preview')
    readonly_fields = ('image_preview',)
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextInputWidget},
    }

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

# Model Admin Classes
@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('description', 'programs_count')
    search_fields = ('description',)
    
    def programs_count(self, obj):
        return obj.programs.count()
    programs_count.short_description = 'Programs Count'

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 60}),
        }

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    form = ProgramForm
    list_display = ('title', 'type', 'category', 'kind', 'start_date', 'end_date', 'is_featured', 'created_at')
    list_filter = ('type', 'category', 'kind', 'target_academic', 'is_featured', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [ProgramRequirementInline, ProgramImageInline]
    readonly_fields = ('created_at', 'updated_at')
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('Basic Information', {
                'fields': ('title', 'description', 'cost', 'url')
            }),
            ('Dates', {
                'fields': ('start_date', 'end_date', 'post_date')
            }),
            ('Categorization', {
                'fields': ('type', 'category', 'audience', 'kind', 'target_academic')
            }),
            ('Media & Status', {
                'fields': ('image', 'is_featured')
            }),
            ('Timestamps', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
        return fieldsets
        
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remove the requirements field from the form since we're using an inline
        if 'requirements' in form.base_fields:
            del form.base_fields['requirements']
        return form
        ('Basic Information', {
            'fields': ('title', 'description', 'cost', 'url')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'post_date')
        }),
        ('Categorization', {
            'fields': ('type', 'category', 'audience', 'kind', 'target_academic')
        }),
        ('Media & Status', {
            'fields': ('image', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'type', 'is_verified', 'date_joined')
    list_filter = ('type', 'gender', 'is_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'program', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'program__title')
    date_hierarchy = 'created_at'

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('status', 'timestamp', 'email_type', 'recipient_count')
    list_filter = ('status', 'timestamp')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    def email_type(self, obj):
        return obj.__class__.__name__
    email_type.short_description = 'Email Type'
    
    def recipient_count(self, obj):
        if hasattr(obj, 'recipients'):
            return obj.recipients.count()
        return 0
    recipient_count.short_description = 'Recipients'

@admin.register(WeeklyEmail)
class WeeklyEmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_date', 'email_sent', 'sent_at', 'users_count', 'programs_count', 'send_now_button')
    list_filter = ('sent_date', 'email_sent')
    filter_horizontal = ('users', 'programs')
    date_hierarchy = 'sent_date'
    search_fields = ('subject',)
    actions = ['send_selected_emails']
    readonly_fields = ('email_sent', 'sent_at', 'send_now_button')
    fieldsets = (
        ('Email Content', {
            'fields': ('subject', 'programs')
        }),
        ('Recipients', {
            'fields': ('users',)
        }),
        ('Scheduling', {
            'fields': ('sent_date', 'email_sent', 'sent_at')
        }),
        ('Actions', {
            'fields': ('send_now_button',),
            'classes': ('collapse',)
        }),
    )
    
    def users_count(self, obj):
        return obj.users.count()
    users_count.short_description = 'Recipients'
    
    def programs_count(self, obj):
        return obj.programs.count()
    programs_count.short_description = 'Programs'
    
    def send_now_button(self, obj):
        if obj.email_sent:
            return 'Already sent'
        return format_html(
            '<a class="button" href="{}?send_now={}">Send Now</a>',
            reverse('admin:activities_weeklyemail_change', args=[obj.id]),
            '1'
        )
    send_now_button.short_description = 'Actions'
    send_now_button.allow_tags = True
    
    def response_change(self, request, obj):
        if 'send_now' in request.GET and not obj.email_sent:
            obj.send_emails()
            self.message_user(request, "Weekly email has been sent to all subscribers.")
            return redirect('admin:activities_weeklyemail_changelist')
        return super().response_change(request, obj)
    
    def send_selected_emails(self, request, queryset):
        count = 0
        for weekly_email in queryset:
            if not weekly_email.email_sent:
                if weekly_email.send_emails():
                    count += 1
        self.message_user(request, f"Successfully sent {count} weekly emails.")
    send_selected_emails.short_description = "Send selected weekly emails"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'confirmed_at', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('confirmation_code', 'confirmed_at', 'unsubscribed_at', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriptions activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} subscriptions deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'

# Register models that don't need custom admin
admin.site.register(ProgramImage)
admin.site.register(ProgramRequirement)

# Register Category and BlogPost if they exist
admin.site.register(Category)
admin.site.register(BlogPost)