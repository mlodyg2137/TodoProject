from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, QueryDict, JsonResponse
from django.shortcuts import get_object_or_404, render

from projects.models import Project
from tasks.models import Task

@login_required
def tasks_page(request):
    projects = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    status_choices = Task.Status.choices
    return render(request, "ui/tasks.html", {"projects": projects, "status_choices": status_choices})


@login_required
def tasks_table(request):
    qs = (Task.objects
          .select_related("project", "owner")
          .prefetch_related("project__members")
          .filter(Q(project__owner=request.user) | Q(project__members=request.user))
          .distinct())

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

    title = (request.POST.get("title") or "").strip()
    project_id = request.POST.get("project")
    status = request.POST.get("status") or Task.Status.TODO

    if not title or not project_id:
        return HttpResponse("Title and project required.", status=400)

    project = get_object_or_404(Project, pk=project_id)

    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Only project owner can create tasks.")

    task = Task.objects.create(project=project, owner=request.user, title=title, status=status)
    return render(request, "ui/_task_row.html", {"t": task})


@login_required
def toggle_done(request, pk: int):
    if request.method not in ("POST", "PATCH"):
        return HttpResponse(status=405)

    task = get_object_or_404(
        Task.objects.select_related("project")
        .filter(Q(project__owner=request.user) | Q(project__members=request.user))
        .distinct(),
        pk=pk,
    )
    if task.project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can modify task.")

    task.status = Task.Status.DONE if task.status != Task.Status.DONE else Task.Status.TODO
    task.save(update_fields=["status", "completed_at", "updated_at"])
    return render(request, "ui/_task_row.html", {"t": task})


@login_required
def delete_task(request, pk: int):
    if request.method != "DELETE":
        return HttpResponse(status=405)

    task = get_object_or_404(
        Task.objects.select_related("project")
        .filter(Q(project__owner=request.user) | Q(project__members=request.user))
        .distinct(),
        pk=pk,
    )
    if task.project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can delete task.")

    task.delete()
    return HttpResponse(status=200)


@login_required
def projects_table(request):
    qs = (Project.objects
          .prefetch_related("members")
          .filter(Q(owner=request.user) | Q(members=request.user))
          .distinct()
          .order_by("id"))
    return render(request, "ui/_projects_table.html", {"projects": qs})


@login_required
def project_create(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    name = (request.POST.get("name") or "").strip()
    if not name:
        return HttpResponse("Project name required.", status=400)

    p = Project.objects.create(name=name, owner=request.user)
    p.members.add(request.user)

    return render(request, "ui/_project_option_and_row.html", {"p": p})


User = get_user_model()

@login_required
def project_add_member(request, pk: int):
    if request.method != "POST":
        return HttpResponse(status=405)

    project = get_object_or_404(
        Project.objects.prefetch_related("members", "owner"),
        pk=pk
    )

    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can manage members.")

    username = (request.POST.get("username") or "").strip()
    if not username:
        return HttpResponse("Username required.", status=400)

    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "ui/_project_members_oob.html", {"p": project, "message": f"Użytkownik \'{username}\' nie istnieje."})

    project.members.add(u)

    return render(request, "ui/_project_members_oob.html", {"p": project, "message": f"Dodano {u.username} do projektu \"{project.name}\"."})


@login_required
def project_remove_member(request, pk: int):
    if request.method != "POST":
        return HttpResponse(status=405)

    project = get_object_or_404(Project.objects.prefetch_related("members", "owner"), pk=pk)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can manage members.")

    username = (request.POST.get("username") or "").strip()
    if not username:
        return render(request, "ui/_project_members_oob.html", {"p": project, "message": "Podaj username."})

    if username == project.owner.username:
        return render(request, "ui/_project_members_oob.html", {"p": project, "message": "Nie można usunąć właściciela projektu."})

    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "ui/_project_members_oob.html", {"p": project, "message": f"Użytkownik '{username}' nie istnieje."})

    if not project.members.filter(pk=u.pk).exists():
        return render(request, "ui/_project_members_oob.html", {"p": project, "message": f"Użytkownik '{u.username}' nie jest członkiem."})

    project.members.remove(u)
    return render(request, "ui/_project_members_oob.html", {"p": project, "message": f"Usunięto {u.username} z projektu „{project.name}”."})


@login_required
def project_delete(request, pk: int):
    if request.method != "POST":
        return HttpResponse(status=405)
    project = get_object_or_404(Project.objects.prefetch_related("members","owner"), pk=pk)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can delete project.")

    row_id = f"project-{project.id}"
    name = project.name
    project.delete()

    return render(request, "ui/_project_deleted_oob.html", {"row_id": row_id, "name": name})

