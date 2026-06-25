from django import forms

from utils import validate_github_url
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "").strip()
        return validate_github_url(github_url)
