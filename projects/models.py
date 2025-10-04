from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_project"
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="projects", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
