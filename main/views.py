from functools import wraps
from zoneinfo import ZoneInfo

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.staticfiles import finders
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from main.forms import AwardForm, ExperienceForm
from main.models import Award, Experience


EXPERIENCE_PUBLIC_FIELDS = (
    "title", "description", "category", "thumbnail", "started_at", "ended_at",
    "organization", "logo_static_path", "logo_alt", "start_year", "start_month",
    "end_year", "end_month", "is_current", "display_order", "source_key",
)


def portfolio_owner_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped_view


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


def editor_or_superuser_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not (request.user.is_superuser or is_editor(request.user)):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped_view


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created. Please log in.")
        return redirect("main:login")

    return render(request, "register.html", {"name": "David Mesakh", "form": form})


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login",
            timezone.localtime(timezone.now(), ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S"),
        )
        return response

    return render(request, "login.html", {"name": "David Mesakh", "form": form})


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


def show_main(request):
    last_login = request.COOKIES.get("last_login") or "No recent login recorded"
    education_list = [
        {
            "institution": "Universitas Indonesia",
            "label": "UNDERGRADUATE STUDENT",
            "description": "Bachelor of Information Systems · Faculty of Computer Science",
            "status": "Present",
            "logo": "img/logo-fasilkom-ui.png",
            "logo_alt": "Logo Fakultas Ilmu Komputer Universitas Indonesia",
        },
        {
            "institution": "SMAS Budhaya II Santo Agustinus",
            "label": "SECONDARY EDUCATION",
            "description": "Science track · Senior High School",
            "status": "2022–2025",
            "logo": "img/logo-smas-budhaya.webp",
            "logo_alt": "Logo SMAS Budhaya II Santo Agustinus",
        },
    ]
    for education in education_list:
        if not finders.find(education["logo"]):
            education["logo"] = None
    context = {
        "education_list": education_list,
        "name": "David Mesakh",
        "last_login": last_login,
        "npm": "2506604503",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            '''
Hello!!! I'm Dave, I'm a 2nd year Information Systems student at Universitas Indonesia.
                        Interested and enthusiastic in turning data into insight, ideas into product. I also love music ^_^!'''
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {"name": "David Mesakh"}
    if request.user.is_superuser:
        context["experience_form"] = ExperienceForm()
    return render(request, "experience.html", context)


def get_experiences_ajax(request):
    query = request.GET.get("title", "").strip()
    queryset = Experience.objects.all()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(organization__icontains=query)
            | Q(category__icontains=query)
        )
    experiences = list(
        queryset.annotate(star_count=Count("starred_by")).order_by("display_order", "id")
    )
    authenticated = request.user.is_authenticated
    can_edit = authenticated and (request.user.is_superuser or is_editor(request.user))
    can_delete = authenticated and request.user.is_superuser
    starred_ids = set()
    if authenticated and experiences:
        starred_ids = set(
            Experience.starred_by.through.objects.filter(
                experience_id__in=[experience.pk for experience in experiences],
                user_id=request.user.pk,
            ).values_list("experience_id", flat=True)
        )

    data = [
        {
            "pk": str(experience.pk),
            "title": experience.title,
            "description": experience.description,
            "description_paragraphs": experience.description_paragraphs,
            "category": experience.category,
            "thumbnail": experience.thumbnail,
            "organization": experience.organization,
            "logo_static_path": experience.logo_static_path,
            "logo_url": static(experience.logo_static_path) if experience.logo_static_path else None,
            "logo_alt": experience.logo_alt,
            "start_year": experience.start_year,
            "start_month": experience.start_month,
            "end_year": experience.end_year,
            "end_month": experience.end_month,
            "is_current": experience.is_current,
            "display_order": experience.display_order,
            "start_period": experience.start_period,
            "end_period": experience.end_period,
            "star_count": experience.star_count,
            "is_starred": experience.pk in starred_ids,
            "can_edit": can_edit,
            "can_delete": can_delete,
            "star_url": reverse("main:toggle_experience_star", args=[experience.pk]) if authenticated else None,
            "edit_url": reverse("main:update_experience", args=[experience.pk]) if can_edit else None,
            "delete_url": reverse("main:delete_experience", args=[experience.pk]) if can_delete else None,
        }
        for experience in experiences
    ]
    return JsonResponse({"is_authenticated": authenticated, "experiences": data})


def get_experiences_json(request):
    experiences = Experience.objects.all().order_by("display_order", "id")
    return HttpResponse(
        serializers.serialize(
            "json",
            experiences,
            fields=EXPERIENCE_PUBLIC_FIELDS,
        ),
        content_type="application/json",
    )


@login_required(login_url="main:login")
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)
    return redirect("main:show_experience")


@login_required(login_url="main:login")
@portfolio_owner_required
def create_experience(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main:show_experience")
    else:
        form = ExperienceForm()

    context = {
        "name": "David Mesakh",
        "form": form,
        "is_update": False,
    }
    return render(request, "experience_form.html", context)


@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse({"message": "You do not have permission to add an Experience."}, status=403)

    form = ExperienceForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    experience = form.save()
    return JsonResponse(
        {"message": "Experience successfully added!", "pk": str(experience.pk)},
        status=201,
    )


@login_required(login_url="main:login")
@editor_or_superuser_required
def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect("main:show_experience")
    else:
        form = ExperienceForm(instance=experience)

    context = {
        "name": "David Mesakh",
        "form": form,
        "experience": experience,
        "is_update": True,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="main:login")
@portfolio_owner_required
@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()
    return redirect("main:show_experience")


def show_awards(request):
    context = {
        "name": "David Mesakh",
        "award_list": Award.objects.all(),
    }
    return render(request, "awards.html", context)


@login_required(login_url="main:login")
@portfolio_owner_required
def create_award(request):
    if request.method == "POST":
        form = AwardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main:show_awards")
    else:
        form = AwardForm()

    return render(request, "add_award.html", {"name": "David Mesakh", "form": form})


@login_required(login_url="main:login")
@portfolio_owner_required
@require_POST
def delete_award(request, award_id):
    award = get_object_or_404(Award, pk=award_id)
    award.delete()
    return redirect("main:show_awards")


def show_json(request):
    data = Award.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_json_by_id(request, id):
    data = Award.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")
