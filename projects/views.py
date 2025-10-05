from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import decorators, response, status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Project
from .serializers import ProjectSerializer

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.none()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["owner", "members"]
    search_fields = ["id", "name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        return Project.objects.filter(
            Q(members=self.request.user) | Q(owner=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    @decorators.action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        qs = self.filter_queryset(self.get_queryset())
        data = qs.values("name").annotate(count=Count("members")).order_by("name")
        return response.Response(list(data), status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], url_path="add_member")
    def add_member(self, request, pk=None):
        try:
            project = self.get_object()
            user_id = request.data.get("user_id")

            if not user_id:
                return response.Response(
                    {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return response.Response(
                    {"error": f"User with id {user_id} does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if user in project.members.all():
                return response.Response(
                    {"detail": "User is already a member of this project"},
                    status=status.HTTP_200_OK,
                )

            project.members.add(user)
            project.save()

            return response.Response(
                {"detail": f"User {user.username} added successfully"},
                status=status.HTTP_200_OK,
            )

        except Project.DoesNotExist:
            return response.Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
