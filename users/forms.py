from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from utils import normalize_phone_number
from .models import User


class RegisterForm(forms.ModelForm):
    """Форма регистрации пользователя"""
    
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "phone", "password")

    def clean_phone(self):
        phone_value = self.cleaned_data.get("phone", "").strip()
        return normalize_phone_number(phone_value)


class LoginForm(forms.Form):
    """Форма входа в систему"""
    
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный email или пароль")
            if not user.is_active:
                raise forms.ValidationError("Аккаунт не активен")
            cleaned_data["user"] = user
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля"""
    
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def clean_phone(self):
        phone_value = self.cleaned_data.get("phone", "").strip()
        return normalize_phone_number(phone_value)

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "").strip()
        
        if not github_url:
            return github_url
        
        parsed_url = urlparse(github_url)
        domain = parsed_url.netloc.lower()
        valid_domain = domain in {"github.com", "www.github.com"}
        valid_scheme = parsed_url.scheme in {"http", "https"}
        
        if not valid_scheme or not valid_domain:
            raise forms.ValidationError("Укажите ссылку на github.com")
        
        return github_url
