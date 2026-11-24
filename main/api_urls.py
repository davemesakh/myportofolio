from django.urls import path
from rest_framework.authtoken import views as authtoken_views

from main.api_views import (
    api_logout,
    experience_detail,
    experience_list,
    experience_star,
)

app_name = "api"

urlpatterns = [
    path("auth/token/", authtoken_views.obtain_auth_token, name="api_token_auth"),
    path("auth/logout/", api_logout, name="api_logout"),
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
