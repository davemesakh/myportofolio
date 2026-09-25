import re
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='full-time'
    )

    thumbnail = models.URLField(
        blank=True,
        null=True
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    ended_at = models.DateTimeField(
        blank=True,
        null=True
    )

    organization = models.CharField(max_length=255, blank=True)
    logo_static_path = models.CharField(max_length=255, blank=True)
    logo_alt = models.CharField(max_length=255, blank=True)
    start_year = models.PositiveSmallIntegerField(null=True, blank=True)
    start_month = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_month = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    is_current = models.BooleanField(null=True, blank=True, default=None)
    display_order = models.PositiveIntegerField(default=0)
    source_key = models.SlugField(unique=True, null=True, blank=True, default=None)
    starred_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="starred_experiences", blank=True
    )

    @property
    def description_paragraphs(self):
        text = self.description.replace("\r\n", "\n").replace("\r", "\n")
        return [part.strip() for part in re.split(r"\n[ \t]*\n+", text) if part.strip()]

    @staticmethod
    def _period(year, month):
        if year is None:
            return None
        months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        if month is not None and 1 <= month <= 12:
            return {"iso": f"{year:04d}-{month:02d}", "label": f"{months[month - 1]} {year}"}
        return {"iso": str(year), "label": str(year)}

    @property
    def start_period(self):
        return self._period(self.start_year, self.start_month)

    @property
    def end_period(self):
        return self._period(self.end_year, self.end_month)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None

class Award(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    achievement = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    description = models.TextField()
    photo_static_path = models.CharField(max_length=255)
    photo_alt = models.CharField(max_length=255)
    photo_width = models.PositiveIntegerField()
    photo_height = models.PositiveIntegerField()
    display_order = models.PositiveIntegerField(default=0)
    source_key = models.SlugField(unique=True, null=True, blank=True, default=None)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title
