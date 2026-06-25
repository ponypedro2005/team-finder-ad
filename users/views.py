from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from constants import PAGINATION, UserFilters
from utils import paginate_queryset
from .forms import LoginForm, ProfileEditForm, RegisterForm
from .models import User

USERS_PER_PAGE = PAGINATION.get("USERS_PER_PAGE", 12)


def register_view(request):
    form = RegisterForm(request.POST or None)
    
    if not form.is_valid():
        return render(request, "users/register.html", {"form": form})
    
    user = form.save(commit=False)
    user.set_password(form.cleaned_data["password"])
    user.save()
    
    login(request, user)
    return redirect("projects:list")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    
    form = LoginForm(request.POST or None)
    
    if form.is_valid():
        user = form.cleaned_data["user"]
        login(request, user)
        return redirect("projects:list")
    
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("projects:list")


def users_list_view(request):
    queryset = User.objects.all()
    active_filter = None
    
    if request.user.is_authenticated:
        filter_type = request.GET.get("filter")
        
        if filter_type == UserFilters.FAVORITE_AUTHORS:
            favorite_projects = request.user.favorites.all()
            queryset = User.objects.filter(
                owned_projects__in=favorite_projects
            ).distinct()
            active_filter = UserFilters.FAVORITE_AUTHORS
            
        elif filter_type == UserFilters.PARTICIPATED_AUTHORS:
            participated_projects = request.user.participated_projects.all()
            queryset = User.objects.filter(
                owned_projects__in=participated_projects
            ).distinct()
            active_filter = UserFilters.PARTICIPATED_AUTHORS
            
        elif filter_type == UserFilters.LIKED_MY_PROJECTS:
            my_projects = request.user.owned_projects.all()
            queryset = User.objects.filter(
                favorites__in=my_projects
            ).distinct()
            active_filter = UserFilters.LIKED_MY_PROJECTS
            
        elif filter_type == UserFilters.MY_PROJECT_PARTICIPANTS:
            my_projects = request.user.owned_projects.all()
            queryset = User.objects.filter(
                participated_projects__in=my_projects
            ).distinct()
            active_filter = UserFilters.MY_PROJECT_PARTICIPANTS
    
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
    user_obj = get_object_or_404(User, id=user_id)
    return render(
        request,
        "users/user-details.html",
        {"user_obj": user_obj},
    )


@login_required
def edit_profile_view(request):
    current_user = request.user
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=current_user,
    )
    
    if not form.is_valid():
        return render(request, "users/edit_profile.html", {"form": form})
    
    form.save()
    return redirect("users:detail", user_id=current_user.id)


@login_required
def change_password_view(request):
    current_user = request.user
    form = PasswordChangeForm(
        user=current_user,
        data=request.POST or None,
    )
    
    if not form.is_valid():
        return render(request, "users/change_password.html", {"form": form})
    
    form.save()
    update_session_auth_hash(request, current_user)
    return redirect("users:detail", user_id=current_user.id)
