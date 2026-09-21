from django.urls import path

from main.views import (
    create_award,
    create_experience,
    delete_award,
    delete_experience,
    get_experiences_json,
    show_awards,
    show_experience,
    show_json,
    show_json_by_id,
    show_main,
    update_experience,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/json/", get_experiences_json, name="get_experiences_json"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("awards/", show_awards, name="show_awards"),
    path("awards/add/", create_award, name="create_award"),
    path("awards/<int:award_id>/delete/", delete_award, name="delete_award"),
    path("json/", show_json, name="show_json"),
    path("json/<int:id>/", show_json_by_id, name="show_json_by_id"),
]
