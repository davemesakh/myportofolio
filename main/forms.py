from django import forms

from main.models import Award, Experience


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = (
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
        )
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Teaching Assistant"}),
            "description": forms.Textarea(attrs={"rows": 6, "placeholder": "Describe your role and contributions."}),
            "organization": forms.TextInput(attrs={"placeholder": "e.g. Universitas Indonesia"}),
            "logo_static_path": forms.TextInput(attrs={"placeholder": "e.g. img/organization-logo.png"}),
            "logo_alt": forms.TextInput(attrs={"placeholder": "Describe the organization logo."}),
            "start_year": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 2026"}),
            "start_month": forms.NumberInput(attrs={"min": 1, "max": 12, "placeholder": "1-12"}),
            "end_year": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 2026"}),
            "end_month": forms.NumberInput(attrs={"min": 1, "max": 12, "placeholder": "1-12"}),
            "display_order": forms.NumberInput(attrs={"min": 0, "placeholder": "e.g. 0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "award-form-control"

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        start_month = cleaned_data.get("start_month")
        end_year = cleaned_data.get("end_year")
        end_month = cleaned_data.get("end_month")
        is_current = cleaned_data.get("is_current")

        if start_month is not None and start_year is None:
            self.add_error("start_month", "Enter a start year when providing a start month.")

        if end_month is not None and end_year is None:
            self.add_error("end_month", "Enter an end year when providing an end month.")

        if is_current is True and (end_year is not None or end_month is not None):
            self.add_error("is_current", "A current experience cannot have an end date.")

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
            self.add_error(None, "The end date cannot be earlier than the start date.")

        return cleaned_data


class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = (
            "title",
            "achievement",
            "year",
            "description",
            "photo_static_path",
            "photo_alt",
            "photo_width",
            "photo_height",
            "display_order",
        )
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Olimpiade Sains Nasional"}),
            "achievement": forms.TextInput(attrs={"placeholder": "e.g. Third Place"}),
            "year": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 2026"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Tell the story behind this achievement."}),
            "photo_static_path": forms.TextInput(attrs={"placeholder": "e.g. img/award-photo.jpeg"}),
            "photo_alt": forms.TextInput(attrs={"placeholder": "Describe the photo for screen-reader users."}),
            "photo_width": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 800"}),
            "photo_height": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 600"}),
            "display_order": forms.NumberInput(attrs={"min": 0, "placeholder": "e.g. 0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "award-form-control"
