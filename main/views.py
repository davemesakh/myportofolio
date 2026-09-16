from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.staticfiles import finders
from django.views.decorators.http import require_POST

from main.forms import AwardForm
from main.models import Award, Experience


def show_main(request):
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
    context = {
        "name": "David Mesakh",
        "experience_list": Experience.objects.all().order_by("display_order", "id"),
    }
    return render(request, "experience.html", context)


def show_awards(request):
    context = {
        "name": "David Mesakh",
        "award_list": Award.objects.all(),
    }
    return render(request, "awards.html", context)


def create_award(request):
    if request.method == "POST":
        form = AwardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main:show_awards")
    else:
        form = AwardForm()

    return render(request, "add_award.html", {"name": "David Mesakh", "form": form})


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
