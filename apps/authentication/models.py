from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class GitHubAccount(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="github_account",
    )

    github_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255)

    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    profile_url = models.URLField()
    avatar_url = models.URLField(blank=True)

    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)

    token_expires_at = models.DateTimeField(null=True, blank=True)
    refresh_token_expires_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username
