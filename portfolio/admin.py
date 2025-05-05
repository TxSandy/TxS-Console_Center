from django.contrib import admin
from .models import ProjectUpload, ContactMessage, Tag


@admin.register(ProjectUpload)
class ProjectUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'slug', 'author__username', 'tags__name')  
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'slug', 'desc', 'live_link', 'github_link', 'image', 'is_published', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.action(description="Mark selected messages as read")
def mark_as_read(modeladmin, request, queryset):
    if queryset.exists():
        queryset.update(is_read=True)


@admin.action(description="Mark selected messages as unread")
def mark_as_unread(modeladmin, request, queryset):
    if queryset.exists():
        queryset.update(is_read=False)


@admin.action(description="Mark as resolved")
def mark_resolved(modeladmin, request, queryset):
    if queryset.exists():
        queryset.update(status='resolved')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone_number', 
        'role', 'status', 'is_read', 'submitted_at'
    )
    list_filter = ('status', 'is_read', 'role', 'submitted_at')
    search_fields = ('first_name', 'last_name', 'email', 'message')
    actions = [mark_as_read, mark_as_unread, mark_resolved]
    readonly_fields = ('submitted_at', 'id')
    ordering = ('-submitted_at',)

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role', 'message')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'is_read', 'id', 'submitted_at'),
            'classes': ('collapse',),
        }),
    )

admin.site.register(Tag)