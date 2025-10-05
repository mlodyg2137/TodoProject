from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    task_name = serializers.ReadOnlyField(source="task.title")

    class Meta:
        model = Comment
        fields = [
            "id",
            "owner",
            "task_name",
            "body",
            "created_at",
        ]
