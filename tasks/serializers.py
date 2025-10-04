from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        model = Task
        fields = ["id", "owner", "project", "project_name", "title", "description", "status", "due_date", "completed_at", "created_at", "updated_at"]