from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from projects.models import Project
from tasks.models import Task


@login_required
def tasks_page(request):
    projects = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    return render(request, "ui/tasks.html", {"projects": projects})


@login_required
def tasks_table(request):
    qs = Task.objects.filter(
        Q(project__owner=request.user) | Q(project__members=request.user)
    ).distinct()

    status = request.GET.get("status")
    proj = request.GET.get("project")
    if status:
        qs = qs.filter(status=status)
    if proj:
        qs = qs.filter(project_id=proj)

    return render(request, "ui/_tasks_table.html", {"tasks": qs})


@login_required
def create_task(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    title = request.POST.get("title", "").strip()
    project_id = request.POST.get("project")
    status = request.POST.get("status", "todo")

    if not title or not project_id:
        return HttpResponse("Title and project required.", status=400)

    project = get_object_or_404(Project, pk=project_id)

    # spójne z API: tworzyć może tylko owner projektu
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Only project owner can create tasks.")

    task = Task.objects.create(project=project, owner=request.user, title=title, status=status)
    # zwracamy gotowy wiersz HTML, który htmx wstawi do tabeli
    return render(request, "ui/_task_row.html", {"t": task})


@login_required
def toggle_done(request, pk: int):
    if request.method not in ("POST", "PATCH"):
        return HttpResponse(status=405)

    task = get_object_or_404(
        Task.objects.filter(
            Q(project__owner=request.user) | Q(project__members=request.user)
        ).distinct(),
        pk=pk,
    )

    # edycja tylko dla ownera projektu (tak jak w permissionach API)
    if task.project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can modify task.")

    task.status = task.Status.DONE if task.status != task.Status.DONE else task.Status.TODO
    task.save(update_fields=["status", "completed_at", "updated_at"])
    return render(request, "ui/_task_row.html", {"t": task})


@login_required
def delete_task(request, pk: int):
    if request.method != "POST":
        return HttpResponse(status=405)

    task = get_object_or_404(
        Task.objects.filter(
            Q(project__owner=request.user) | Q(project__members=request.user)
        ).distinct(),
        pk=pk,
    )

    if task.project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can delete task.")

    task.delete()
    # htmx: 204 + hx-trigger w kliencie usunie wiersz (albo zwróć pusty wiersz)
    return HttpResponse(status=204)
