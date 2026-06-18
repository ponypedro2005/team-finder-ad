from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Открыт')
        CLOSED = 'closed', _('Закрыт')

    # Константы для максимальной длины полей
    NAME_MAX_LENGTH = 200
    STATUS_MAX_LENGTH = max(len(status) for status, _ in Status.choices)

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name=_('Название')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name=_('Владелец')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Ссылка на GitHub')
    )
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_('Статус')
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name=_('Участники')
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')

    def __str__(self):
        return self.name

    def participant_count(self):
        return self.participants.count()
