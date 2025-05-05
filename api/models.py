from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
import shortuuid 
from portfolio.models import Tag as model

# Create your models here.


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Required when creating superusers

    def __str__(self):
        return self.email  # Better if you want email as unique identity

    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError("Users must have an email address")

        email_username = self.email.split("@")[0]
        if not self.full_name:
            self.full_name = email_username
        if not self.username:
            self.username = email_username

        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to="image", default="default/default-user.jpg", null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.CharField(max_length=100, null=True, blank=True)
    about = models.CharField(max_length=100, null=True, blank=True)
    author = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    github_id = models.CharField(max_length=100, null=True, blank=True)
    portfolio = models.CharField(max_length=100, null=True, blank=True)
    telegram_id = models.CharField(max_length=100, null=True, blank=True)
    linkedin_id = models.CharField(max_length=100, null=True, blank=True)
    discord_id = models.CharField(max_length=100, null=True, blank=True)
    instagram_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.full_name

        super(Profile, self).save(*args, **kwargs)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user = instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="image", null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Category"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)
    
    def post_count(self):
        return Post.objects.filter(category=self).count()

class Post(models.Model):
    STATUS = ( 
        ("Active", "Active"), 
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="image", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField("portfolio.Tag", blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    status = models.CharField(max_length=100, choices=STATUS, default="Active")
    view = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="likes_user")
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Post"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + shortuuid.uuid()[:5]
        super(Post, self).save(*args, **kwargs)
    
    def comments(self):
        return Comment.objects.filter(post=self).order_by("-id")


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    comment = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Comment"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Bookmark"


class Notification(models.Model):
    NOTIFICATION_TYPE = (
    ("Like", "Like"),
    ("Comment", "Comment"),
    ("Bookmark", "Bookmark"),
)


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    type = models.CharField(choices=NOTIFICATION_TYPE, max_length=100)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.post:
            return f"{self.post.title} - {self.type}"
        else:
            return "Notification"
        
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Notification"