from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from utils import paginate_queryset

from .forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from .models import User

USERS_PER_PAGE = 12

FILTER_FAVORITE_AUTHORS = "favorite_authors"
FILTER_PARTICIPATED_AUTHORS = "participated_authors"
FILTER_LIKED_MY_PROJECTS = "liked_my_projects"
FILTER_MY_PROJECT_PARTICIPANTS = "my_project_participants"


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            registered_user = form.save()
            login(request, registered_user)
            return redirect("projects:list")
    else:
        form = RegisterForm()

    return render(
        request,
        "users/register.html",
        {"form": form},
    )


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("projects:list")
    else:
        form = LoginForm()

    return render(
        request,
        "users/login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("projects:list")


def users_list_view(request):
    queryset = User.objects.order_by("-id")
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        if active_filter == FILTER_FAVORITE_AUTHORS:
            favorite_ids = request.user.favorites.values_list("id", flat=True)
            queryset = queryset.filter(owned_projects__id__in=favorite_ids).distinct()

        elif active_filter == FILTER_PARTICIPATED_AUTHORS:
            participated_ids = request.user.participated_projects.values_list(
                "id", flat=True
            )
            queryset = queryset.filter(
                owned_projects__id__in=participated_ids
            ).distinct()

        elif active_filter == FILTER_LIKED_MY_PROJECTS:
            my_project_ids = request.user.owned_projects.values_list("id", flat=True)
            queryset = (
                queryset.filter(favorites__id__in=my_project_ids)
                .exclude(id=request.user.id)
                .distinct()
            )

        elif active_filter == FILTER_MY_PROJECT_PARTICIPANTS:
            my_project_ids = request.user.owned_projects.values_list("id", flat=True)
            queryset = (
                queryset.filter(participated_projects__id__in=my_project_ids)
                .exclude(id=request.user.id)
                .distinct()
            )

    page_obj = paginate_queryset(request, queryset, USERS_PER_PAGE)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "active_filter": active_filter,
        },
    )


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects"),
        id=user_id,
    )

    return render(
        request,
        "users/user-details.html",
        {"user": profile_user},
    )


@login_required
def edit_profile_view(request):
    current_user = request.user

    if request.method == "POST":
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=current_user,
        )
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=current_user.id)
    else:
        form = ProfileEditForm(instance=current_user)

    return render(
        request,
        "users/edit_profile.html",
        {"form": form},
    )


@login_required
def change_password_view(request):
    current_user = request.user

    if request.method == "POST":
        form = UserPasswordChangeForm(current_user, request.POST)
        if form.is_valid():
            updated_user = form.save()
            update_session_auth_hash(request, updated_user)
            return redirect("users:detail", user_id=current_user.id)
    else:
        form = UserPasswordChangeForm(current_user)

    return render(
        request,
        "users/change_password.html",
        {"form": form},
    )
