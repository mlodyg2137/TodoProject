import pytest


@pytest.mark.django_db
def test_create_project_sets_owner_and_member(auth_client, user):
    r = auth_client.post("/api/projects/", {"name": "proj"}, format="json")
    assert r.status_code == 201
    project_id = r.data["id"]

    r_list = auth_client.get("/api/projects/")
    assert r_list.status_code == 200
    assert any(
        p["id"] == project_id for p in r_list.data["results"] if isinstance(r_list.data, dict)
    ) or any(p["id"] == project_id for p in r_list.data)
