from django.db import models
import uuid
from django.utils.text import slugify
from api.models import User
from phonenumber_field.modelfields import PhoneNumberField



class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ProjectUpload(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    live_link = models.CharField(max_length=255)
    guthub_link = models.CharField(max_length=255)
    desc = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='tags', blank=True)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    
class ContactMessage(models.Model):
    ROLE_CHOICES = [
        ("Client", "As a Client"),
        ("Frontend Developer", "As a Frontend Developer"),
        ("Backend Developer", "As a Backend Developer"),
        ("Full Stack Developer", "As a Full Stack Developer"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role}) - {self.status}"