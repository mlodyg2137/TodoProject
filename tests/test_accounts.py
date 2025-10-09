import pytest


@pytest.mark.django_db
def test_register_creates_user(api_client):
    payload = {
        "email": "user@ex.com",
        "username": "user",
        "password": "pass12345",
        "re_password": "pass12345",
    }
    r = api_client.post("/api/auth/users/", payload, format="json")
    assert r.status_code == 201
    assert r.data["username"] == "user"


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    r = api_client.get("/api/auth/users/me/")
    assert r.status_code == 401  # Unauthorized


@pytest.mark.django_db
def test_me_returns_profile(auth_client, user):
    r = auth_client.get("/api/auth/users/me/")
    assert r.status_code == 200
    assert r.data["username"] == user.username
