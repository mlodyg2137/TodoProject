import pytest

from projects.models import Project
from tasks.models import Task


@pytest.mark.django_db
def test_member_can_comment(auth_client, user, user2):
    p = Project.objects.create(name="P", owner=user)
    p.members.add(user, user2)
    t = Task.objects.create(project=p, owner=user, title="T", status="todo")

    r = auth_client.post("/api/comments/", {"task": t.id, "body": "some comment"}, format="json")
    assert r.status_code == 201


@pytest.mark.django_db
def test_non_member_cannot_comment(auth_client_user2, user):
    p = Project.objects.create(name="P", owner=user)
    p.members.add(user)
    t = Task.objects.create(project=p, owner=user, title="T", status="todo")

    r = auth_client_user2.post(
        "/api/comments/", {"task": t.id, "body": "some comment"}, format="json"
    )
    assert r.status_code in (403, 400)
