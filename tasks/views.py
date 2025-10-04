from django.shortcuts import render
from .serializers import TaskSerializer
from .models import Task
from rest_framework import viewsets, decorators, response, status
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsProjectMember
from django.db.models import Count

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsProjectMember]
    filterset_fields = ["status", "project", "due_date"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "title"]

    def get_queryset(self):
        return Task.objects.filter(project__members=self.request.user) | Task.objects.filter(project__owner=self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    
    @decorators.action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        qs = self.filter_queryset(self.get_queryset())
        data = qs.values("status").annotate(count=Count("id")).order_by("status")
        return response.Response(list(data), status=status.HTTP_200_OK)
