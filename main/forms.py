from django import forms

from main.models import Award


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
