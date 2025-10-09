from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import FormView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MeSerializer, RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(MeSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)


class SignupView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
