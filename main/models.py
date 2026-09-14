import uuid
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

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    technologies = models.CharField(max_length=255)
    project_url = models.URLField(blank=True)
    created_at = models.DateField()

    def __str__(self):
        return self.title


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
