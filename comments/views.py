from django.db.models import Count, Q
from rest_framework import decorators, response, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsProjectMemberRead_OwnerWrite

from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectMemberRead_OwnerWrite]
    filterset_fields = ["owner", "task"]
    search_fields = ["id"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(
            Q(owner=user) | Q(task__project__members=user) | Q(task__project__owner=user)
        ).distinct()

    def perform_create(self, serializer):
        u = self.request.user
        task = serializer.validated_data["task"]
        is_owner = task.project.owner == u.id
        is_member = task.project.members.filter(pk=u.pk).exists()
        if not (is_owner or is_member):
            raise PermissionDenied("You are not member of this project.")
        return serializer.save(owner=self.request.user)

    @decorators.action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        qs = self.filter_queryset(self.get_queryset())
        data = qs.values("owner").annotate(count=Count("id")).order_by("owner")
        return response.Response(list(data), status=status.HTTP_200_OK)
