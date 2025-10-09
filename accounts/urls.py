from django.urls import path

from .views import MeView, RegisterView, SignupView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("signup/", SignupView.as_view(), name="signup"),
]
