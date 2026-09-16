from django.urls import path

from main.views import (
    create_award,
    delete_award,
    show_awards,
    show_experience,
    show_json,
    show_json_by_id,
    show_main,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("awards/", show_awards, name="show_awards"),
    path("awards/add/", create_award, name="create_award"),
    path("awards/<int:award_id>/delete/", delete_award, name="delete_award"),
    path("json/", show_json, name="show_json"),
    path("json/<int:id>/", show_json_by_id, name="show_json_by_id"),
]
