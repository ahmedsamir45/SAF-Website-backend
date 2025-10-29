from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib import messages
from django.contrib.messages import SUCCESS, WARNING, ERROR
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from django import forms
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
import logging

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
    EmailStatus,
    NewsletterSubscription
)

logger = logging.getLogger(__name__)

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
    list_display = (
        'subject', 
        'scheduled_for', 
        'get_status_display', 
        'sent_at', 
        'subscribers_count', 
        'programs_count',
        'success_count',
        'failure_count',
        'send_now_button'
    )
    list_filter = ('status', 'scheduled_for')
    filter_horizontal = ('subscribers', 'programs')
    date_hierarchy = 'scheduled_for'
    search_fields = ('subject', 'content', 'last_error')
    actions = ['send_selected_emails']
    readonly_fields = (
        'status', 'sent_at', 'send_now_button', 
        'success_count', 'failure_count', 'last_error',
        'created_at', 'updated_at', 'status_display'
    )
    fieldsets = (
        ('Email Content', {
            'fields': ('subject', 'content', 'programs')
        }),
        ('Scheduling', {
            'fields': (
                'scheduled_for',
                'status',
                ('success_count', 'failure_count'),
                'last_error',
                'sent_at'
            )
        }),
        ('Recipients', {
            'fields': ('subscribers',)
        }),
        ('System Information', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
        ('Actions', {
            'fields': ('send_now_button',),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20
    save_on_top = True
    save_as = True
    view_on_site = False
    
    # Remove custom media to use default admin styling
    
    def status_display(self, obj):
        """Simple status display without custom styling"""
        return obj.get_status_display()
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def subscribers_count(self, obj):
        return obj.subscribers.count()
    subscribers_count.short_description = 'Subscribers'
    
    def programs_count(self, obj):
        return obj.programs.count()
    programs_count.short_description = 'Programs'
    
    def send_now_button(self, obj):
        """Simple send now button with default styling"""
        if obj.status in [EmailStatus.SENT, EmailStatus.SENDING]:
            return obj.get_status_display()
            
        return format_html(
            '<a href="{}?send_now=1" class="default">Send Now</a>',
            reverse('admin:activities_weeklyemail_change', args=[obj.id])
        )
    send_now_button.short_description = 'Actions'
    send_now_button.allow_tags = True
    
    def response_change(self, request, obj):
        """Handle the send now action with simple confirmation"""
        if 'send_now' in request.GET:
            if obj.status in [EmailStatus.SENT, EmailStatus.SENDING]:
                self.message_user(
                    request,
                    f"Email is already in '{obj.get_status_display()}' state.",
                    level=WARNING
                )
            else:
                try:
                    success = obj.send_emails()
                    if success:
                        self.message_user(
                            request,
                            f"Email sent to {obj.success_count} subscribers.",
                            level=SUCCESS
                        )
                    else:
                        self.message_user(
                            request,
                            f"Email sent with {obj.failure_count} failures. {obj.last_error[:200] if obj.last_error else ''}",
                            level=WARNING
                        )
                except Exception as e:
                    self.message_user(
                        request,
                        f"Error sending email: {str(e)}",
                        level=ERROR
                    )
            return redirect('admin:activities_weeklyemail_changelist')
        return super().response_change(request, obj)
        
    def confirm_send_page(self, request, obj):
        """Show a confirmation page before sending"""
        opts = self.model._meta
        app_label = opts.app_label
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Are you sure?',
            'object': obj,
            'opts': opts,
            'app_label': app_label,
            'subscribers_count': obj.subscribers.count(),
            'is_popup': False,
            'media': self.media,
        }
        
        return TemplateResponse(
            request,
            'admin/activities/weeklyemail/confirm_send.html',
            context
        )
        
    def send_selected_emails(self, request, queryset):
        """
        Admin action to send multiple selected emails with confirmation
        """
        # Filter out emails that can't be sent
        sendable_emails = queryset.exclude(
            status__in=[EmailStatus.SENT, EmailStatus.SENDING]
        )
        
        if not sendable_emails.exists():
            self.message_user(
                request,
                "No emails to send. All selected emails are either already sent or being sent.",
                level=WARNING
            )
            return
            
        # Show confirmation page if this is not a POST request
        if request.method != 'POST':
            opts = self.model._meta
            context = {
                **self.admin_site.each_context(request),
                'title': 'Are you sure?',
                'objects': sendable_emails,
                'opts': opts,
                'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            }
            
            return TemplateResponse(
                request,
                'admin/activities/weeklyemail/confirm_bulk_send.html',
                context
            )
            
        # Process the form submission
        sent_count = 0
        failed_count = 0
        
        for email in sendable_emails:
            try:
                if email.send_emails():
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error sending email {email.id}: {str(e)}", exc_info=True)
                failed_count += 1
        
        # Show results
        messages = []
        if sent_count:
            messages.append(f"Successfully sent {sent_count} email{'s' if sent_count > 1 else ''}.")
        if failed_count:
            messages.append(f"Failed to send {failed_count} email{'s' if failed_count > 1 else ''}.")
        
        if messages:
            level = SUCCESS if not failed_count else WARNING
            self.message_user(request, ' '.join(messages), level=level)
        
        # Return to changelist
        return None
        
    send_selected_emails.short_description = "Send selected emails now"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in [EmailStatus.SENT, EmailStatus.SENDING]:
            return [f.name for f in self.model._meta.fields] + ['send_now_button']
        return super().get_readonly_fields(request, obj)
    
    class Media:
        css = {
            'all': ('admin/css/email_admin.css',)
        }
        js = ('admin/js/email_admin.js',)
    
    # send_selected_emails method is already defined above with more comprehensive functionality
    send_selected_emails.short_description = "Send selected emails now"

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
    list_display = ('email', 'is_active', 'created_at', 'unsubscribed_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('unsubscribed_at', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f'{updated} subscriptions activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def deactivate_subscriptions(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} subscriptions deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'

# Register models that don't need custom admin
admin.site.register(ProgramImage)
admin.site.register(ProgramRequirement)

# Register Category and BlogPost if they exist
admin.site.register(Category)
admin.site.register(BlogPost)