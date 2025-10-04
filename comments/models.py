from django.db import models
from django.conf import settings

class Comment(models.Model):
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
