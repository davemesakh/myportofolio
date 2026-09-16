from django.urls import path

from main.views import create_award, delete_award, show_main, show_experience, show_awards

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("awards/", show_awards, name="show_awards"),
    path("awards/add/", create_award, name="create_award"),
    path("awards/<int:award_id>/delete/", delete_award, name="delete_award"),
]
