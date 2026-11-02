from django.urls import path

from main.api_views import experience_detail, experience_list, experience_star

app_name = "api"

urlpatterns = [
    path("experiences/", experience_list, name="experience-list"),
    path(
        "experiences/<uuid:experience_id>/",
        experience_detail,
        name="experience-detail",
    ),
    path(
        "experiences/<uuid:experience_id>/star/",
        experience_star,
        name="experience-star",
    ),
]
