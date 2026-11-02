from django.utils.html import strip_tags
from rest_framework import serializers

from main.image_utils import (
    resolve_experience_logo_url,
    validate_experience_logo_source,
)
from main.models import Experience


class ExperienceSerializer(serializers.ModelSerializer):
    """Expose the form's portfolio fields with read-only identity/display data.

    Paragraphs and periods reuse model properties for card rendering; logo_url
    reuses the safe image resolver. Stars expose only a count and viewer state.
    Timestamps, import identity, and the user relationship are excluded.
    """

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    description_paragraphs = serializers.ReadOnlyField()
    start_period = serializers.ReadOnlyField()
    end_period = serializers.ReadOnlyField()
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = (
            "id",
            "title",
            "description",
            "category",
            "organization",
            "logo_static_path",
            "logo_alt",
            "start_year",
            "start_month",
            "end_year",
            "end_month",
            "is_current",
            "display_order",
            "star_count",
            "is_starred",
            "description_paragraphs",
            "start_period",
            "end_period",
            "logo_url",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "logo_static_path": {"validators": [validate_experience_logo_source]},
        }

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return False
        return obj.starred_by.filter(pk=user.pk).exists()

    def get_logo_url(self, obj):
        return resolve_experience_logo_url(obj.logo_static_path)

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot contain only HTML tags.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Description cannot contain only HTML tags.")
        return value

    def validate_organization(self, value):
        return strip_tags(value).strip()

    def validate_logo_alt(self, value):
        return strip_tags(value).strip()

    def validate(self, attrs):
        # Omitted update fields retain their instance values; explicit nulls
        # remain null. Do not add retained fields to the update payload.
        def retained_value(field):
            return attrs.get(field, getattr(self.instance, field, None))

        start_year = retained_value("start_year")
        start_month = retained_value("start_month")
        end_year = retained_value("end_year")
        end_month = retained_value("end_month")
        is_current = retained_value("is_current")
        errors = {}

        if start_month is not None and start_year is None:
            errors["start_month"] = ["Enter a start year when providing a start month."]
        if end_month is not None and end_year is None:
            errors["end_month"] = ["Enter an end year when providing an end month."]
        if is_current is True and (end_year is not None or end_month is not None):
            errors["is_current"] = ["A current experience cannot have an end date."]

        end_precedes_start = (
            start_year is not None
            and end_year is not None
            and (
                end_year < start_year
                or (
                    end_year == start_year
                    and start_month is not None
                    and end_month is not None
                    and end_month < start_month
                )
            )
        )
        if end_precedes_start:
            errors["non_field_errors"] = [
                "The end date cannot be earlier than the start date."
            ]
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
