from django.shortcuts import redirect
from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("projects/list/", views.project_list_view, name="list"),
    path("project/list/", lambda request: redirect("projects:list")),
    path("projects/<int:project_id>/", views.project_detail_view, name="detail"),
    path(
        "projects/<int:project_id>/toggle-participate/",
        views.toggle_participation_view,
        name="toggle_participate",
    ),
    path(
        "projects/<int:project_id>/complete/",
        views.complete_project_view,
        name="complete_project",
    ),
    path(
        "projects/create-project/",
        views.create_project_view,
        name="create_project",
    ),
    path(
        "projects/<int:project_id>/edit/",
        views.edit_project_view,
        name="edit_project",
    ),
    path("projects/favorites/", views.favorite_projects_view, name="favorites"),
    path(
        "projects/<int:project_id>/toggle-favorite/",
        views.toggle_favorite_view,
        name="toggle_favorite",
    ),
]
