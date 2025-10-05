from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    members = serializers.SlugRelatedField(many=True, read_only=True, slug_field="username")

    class Meta:
        model = Project
        fields = ["id", "name", "owner", "created_at", "members"]
