import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user1", password="pass12345", email="u1@ex.com")


@pytest.fixture
def user2(db):
    return User.objects.create_user(username="user2", password="pass12345", email="u2@ex.com")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def auth_client_user2(api_client, user2):
    client = APIClient()
    token = RefreshToken.for_user(user2).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
