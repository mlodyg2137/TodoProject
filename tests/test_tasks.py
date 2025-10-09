import pytest

from projects.models import Project
from tasks.models import Task


@pytest.fixture
def project_owned_by_user(user):
    p = Project.objects.create(name="P1", owner=user)
    p.members.add(user)
    return p


@pytest.fixture
def project_owned_by_user2(user2):
    p = Project.objects.create(name="P2", owner=user2)
    p.members.add(user2)
    return p


@pytest.mark.django_db
def test_create_task_sets_owner(auth_client, user, project_owned_by_user):
    payload = {"project": project_owned_by_user.id, "title": "Zad1", "status": "todo"}
    r = auth_client.post("/api/tasks/", payload, format="json")
    assert r.status_code == 201
    t = Task.objects.get(id=r.data["id"])
    assert t.owner_id == user.id
    assert t.project_id == project_owned_by_user.id


@pytest.mark.django_db
def test_list_only_my_projects_tasks(
    auth_client, user, project_owned_by_user, user2, project_owned_by_user2
):
    Task.objects.create(project=project_owned_by_user, owner=user, title="task1", status="todo")
    Task.objects.create(project=project_owned_by_user2, owner=user2, title="task2", status="todo")

    r = auth_client.get("/api/tasks/")
    assert r.status_code == 200
    titles = [it.get("title") for it in (r.data["results"] if isinstance(r.data, dict) else r.data)]
    assert "task1" in titles
    assert "task2" not in titles


@pytest.mark.django_db
def test_cannot_create_task_in_foreign_project(auth_client, project_owned_by_user2):
    payload = {"project": project_owned_by_user2.id, "title": "task1", "status": "todo"}
    r = auth_client.post("/api/tasks/", payload, format="json")
    assert r.status_code in (403, 400)


@pytest.mark.django_db
def test_member_can_read_owner_only_write(
    auth_client, auth_client_user2, user, user2, project_owned_by_user
):
    project_owned_by_user.members.add(user2)
    t = Task.objects.create(project=project_owned_by_user, owner=user, title="X", status="todo")

    r_get = auth_client_user2.get(f"/api/tasks/{t.id}/")
    assert r_get.status_code == 200

    r_patch = auth_client_user2.patch(f"/api/tasks/{t.id}/", {"title": "Y"}, format="json")
    assert r_patch.status_code == 403

    r_patch_owner = auth_client.patch(f"/api/tasks/{t.id}/", {"title": "Y"}, format="json")
    assert r_patch_owner.status_code == 200


@pytest.mark.django_db
def test_stats_endpoint(auth_client, user, project_owned_by_user):
    Task.objects.create(project=project_owned_by_user, owner=user, title="A", status="todo")
    Task.objects.create(project=project_owned_by_user, owner=user, title="B", status="done")
    r = auth_client.get("/api/tasks/stats/")
    assert r.status_code == 200
    statuses = {row["status"]: row["count"] for row in r.data}
    assert statuses.get("todo", 0) >= 1
    assert statuses.get("done", 0) >= 1
