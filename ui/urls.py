from django.urls import path

from . import views

app_name = "ui"

urlpatterns = [
    path("", views.tasks_page, name="tasks_page"),
    path("ui/tasks/table/", views.tasks_table, name="tasks_table"),
    path("ui/tasks/create/", views.create_task, name="create_task"),
    path("ui/tasks/<int:pk>/toggle/", views.toggle_done, name="toggle_done"),
    path("ui/tasks/<int:pk>/delete/", views.delete_task, name="delete_task"),
]
