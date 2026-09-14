from django.contrib import admin

from main.models import Award, Experience


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "category", "start_year", "is_current", "display_order")
    search_fields = ("title", "organization", "description", "source_key")
    list_filter = ("category", "is_current", "start_year")
    ordering = ("display_order", "id")


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ("title", "achievement", "year", "display_order")
    search_fields = ("title", "achievement", "description", "source_key")
    list_filter = ("year",)
    ordering = ("display_order", "id")
