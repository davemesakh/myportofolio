from django.shortcuts import render

from main.models import Experience


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
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)