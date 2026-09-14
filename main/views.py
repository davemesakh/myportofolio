from django.shortcuts import render

from main.models import Award, Experience, Project


def show_main(request):
    context = {
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


def show_projects(request):
    context = {
        "name": "David Mesakh",
        "project_list": Project.objects.all().order_by("-created_at", "-id"),
    }
    return render(request, "projects.html", context)


def show_awards(request):
    context = {
        "name": "David Mesakh",
        "award_list": Award.objects.all(),
    }
    return render(request, "awards.html", context)
