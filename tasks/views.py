from django.db.models import Count, Q
from rest_framework import decorators, response, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsProjectMemberRead_OwnerWrite

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsProjectMemberRead_OwnerWrite]
    filterset_fields = ["status", "project", "due_date"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "title"]

    def get_queryset(self):
        return Task.objects.filter(
            Q(project__members=self.request.user) | Q(project__owner=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.owner_id != self.request.user.id:
            raise PermissionDenied("Only project owner can create tasks.")
        return serializer.save(owner=self.request.user)

    @decorators.action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        qs = self.filter_queryset(self.get_queryset())
        data = qs.values("status").annotate(count=Count("id")).order_by("status")
        return response.Response(list(data), status=status.HTTP_200_OK)
