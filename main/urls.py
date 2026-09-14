from django.urls import path

from main.views import show_main, show_experience, show_projects, show_awards

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("awards/", show_awards, name="show_awards"),
]
