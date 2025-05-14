from django.db import models

# Create your models here.
class Visitor(models.Model):
    ip = models.GenericIPAddressField()
    location = models.JSONField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=1)
    last_visited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ip