from rest_framework import serializers

from tasks.models import Task

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())

    class Meta:
        model = Comment
        fields = [
            "id",
            "owner",
            "task",
            "body",
            "created_at",
        ]
