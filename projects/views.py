from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from constants import PAGINATION
from utils import paginate_queryset
from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = PAGINATION.get("PROJECTS_PER_PAGE", 12)


def project_list_view(request):
    queryset = Project.objects.select_related("owner")
    page_obj = paginate_queryset(request, queryset, PROJECTS_PER_PAGE)
    
    return render(
        request,
        "projects/project_list.html",
        {"projects": page_obj},
    )


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        id=project_id,
    )
    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@require_POST
@login_required
def complete_project_view(request, project_id):
    project_obj = get_object_or_404(Project, id=project_id)

    if project_obj.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Только владелец может завершить проект"},
            status=HTTPStatus.FORBIDDEN,
        )

    if project_obj.status != Project.Status.OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже завершен"},
            status=HTTPStatus.BAD_REQUEST,
        )

    project_obj.status = Project.Status.CLOSED
    project_obj.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "project_status": project_obj.status,
        },
        status=HTTPStatus.OK,
    )


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    
    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )
    
    project_obj = form.save(commit=False)
    project_obj.owner = request.user
    project_obj.save()
    project_obj.participants.add(request.user)
    
    return redirect("projects:detail", project_id=project_obj.id)


@login_required
def edit_project_view(request, project_id):
    project_obj = get_object_or_404(Project, id=project_id)

    if project_obj.owner != request.user:
        return redirect("projects:detail", project_id=project_obj.id)

    form = ProjectForm(request.POST or None, instance=project_obj)
    
    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True, "project": project_obj},
        )
    
    updated_project = form.save()
    return redirect("projects:detail", project_id=updated_project.id)


@require_POST
@login_required
def toggle_participate_view(request, project_id):
    project_obj = get_object_or_404(Project, id=project_id)
    
    is_participant = project_obj.participants.filter(id=request.user.id).exists()
    
    if is_participant:
        project_obj.participants.remove(request.user)
    else:
        project_obj.participants.add(request.user)
    
    return JsonResponse(
        {
            "status": "ok",
            "is_participant": not is_participant,
            "participants_count": project_obj.participants.count(),
        },
        status=HTTPStatus.OK,
    )


@require_POST
@login_required
def toggle_favorite_view(request, project_id):
    project_obj = get_object_or_404(Project, id=project_id)
    in_favorites = request.user.favorites.filter(id=project_obj.id).exists()
    
    if in_favorites:
        request.user.favorites.remove(project_obj)
    else:
        request.user.favorites.add(project_obj)
    
    return JsonResponse(
        {
            "status": "ok",
            "favorited": not in_favorites,
        },
        status=HTTPStatus.OK,
    )


@login_required
def favorite_projects_view(request):
    queryset = (
        request.user.favorites
        .select_related("owner")
        .prefetch_related("participants")
    )
    page_obj = paginate_queryset(request, queryset, PROJECTS_PER_PAGE)
    
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": page_obj},
    )
