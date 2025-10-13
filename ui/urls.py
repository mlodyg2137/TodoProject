from django.urls import path

from . import views

app_name = "ui"

urlpatterns = [
    path("", views.tasks_page, name="tasks_page"),
    path("ui/tasks/table/", views.tasks_table, name="tasks_table"),
    path("ui/tasks/create/", views.create_task, name="create_task"),
    path("ui/tasks/<int:pk>/toggle/", views.toggle_done, name="toggle_done"),
    path("ui/tasks/<int:pk>/delete/", views.delete_task, name="delete_task"),

    path("ui/projects/table/", views.projects_table, name="projects_table"),
    path("ui/projects/create/", views.project_create, name="project_create"),
    path("ui/projects/<int:pk>/add-member/", views.project_add_member, name="project_add_member"),
    path("ui/projects/<int:pk>/remove-member/", views.project_remove_member, name="project_remove_member"),
    path("ui/projects/<int:pk>/delete/", views.project_delete, name="project_delete"),

]
