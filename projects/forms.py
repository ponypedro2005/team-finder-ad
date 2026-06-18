from django import forms

from projects.models import Project


class ProjectForm(forms.ModelForm):
    STATUS_DISPLAY_CHOICES = [
        (Project.STATUS_OPEN, "Открыт"),
        (Project.STATUS_CLOSED, "Закрыт"),
    ]

    status = forms.ChoiceField(label="Статус", choices=STATUS_DISPLAY_CHOICES)

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название",
            "description": "Описание",
            "github_url": "Ссылка на GitHub",
        }
