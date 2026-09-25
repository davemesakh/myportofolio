from collections import Counter
from functools import wraps
from zoneinfo import ZoneInfo

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.staticfiles import finders
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
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
    json_response = get_experiences_json(request)
    serialized_experiences = json_response.content.decode("utf-8")
    experience_list = [
        deserialized.object
        for deserialized in serializers.deserialize("json", serialized_experiences)
    ]
    star_counts = Counter()
    starred_experience_ids = set()
    if experience_list:
        star_rows = Experience.starred_by.through.objects.filter(
            experience_id__in=[experience.id for experience in experience_list]
        ).values_list("experience_id", "user_id")
        for experience_id, user_id in star_rows:
            star_counts[experience_id] += 1
            if request.user.is_authenticated and user_id == request.user.pk:
                starred_experience_ids.add(experience_id)
    for experience in experience_list:
        experience.star_count = star_counts[experience.id]
        experience.is_starred_by_user = experience.id in starred_experience_ids

    context = {
        "name": "David Mesakh",
        "experience_list": experience_list,
    }
    return render(request, "experience.html", context)


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


@login_required(login_url="main:login")
@portfolio_owner_required
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
