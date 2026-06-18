from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        CLOSED = 'closed', _('Closed')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=6, 
        choices=Status.choices, 
        default=Status.OPEN
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='participated_projects', 
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def participant_count(self):
        return self.participants.count()
