from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from utils import PHONE_PATTERN, normalize_phone_number

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )
    repeat_password = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "phone")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
            "phone": "Телефон",
        }

    def clean_phone(self):
        phone_value = (self.cleaned_data.get("phone") or "").strip()

        if not PHONE_PATTERN.match(phone_value):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )

        return normalize_phone_number(phone_value)

    def clean(self):
        cleaned_data = super().clean()
        first_password = cleaned_data.get("password")
        second_password = cleaned_data.get("repeat_password")

        if first_password and second_password and first_password != second_password:
            raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data

    def save(self, commit=True):
        new_user = super().save(commit=False)
        new_user.set_password(self.cleaned_data["password"])

        if commit:
            new_user.save()

        return new_user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        email_value = cleaned_data.get("email")
        password_value = cleaned_data.get("password")

        if not email_value or not password_value:
            return cleaned_data

        authenticated_user = authenticate(
            email=email_value,
            password=password_value,
        )
        if authenticated_user is None:
            raise forms.ValidationError("Неверный email или пароль")

        self.user = authenticated_user
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "name",
            "surname",
            "avatar",
            "about",
            "email",
            "phone",
            "github_url",
        )
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "email": "Email",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
        }

    def clean_phone(self):
        phone_value = (self.cleaned_data.get("phone") or "").strip()

        if not PHONE_PATTERN.match(phone_value):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )

        normalized_phone = normalize_phone_number(phone_value)
        duplicate_phone = (
            User.objects.exclude(pk=self.instance.pk)
            .filter(phone=normalized_phone)
            .exists()
        )

        if duplicate_phone:
            raise forms.ValidationError("Этот номер телефона уже используется")

        return normalized_phone

    def clean_github_url(self):
        github_url = (self.cleaned_data.get("github_url") or "").strip()

        if not github_url:
            return github_url

        parsed_url = urlparse(github_url)
        domain = parsed_url.netloc.lower()

        valid_domain = domain in {"github.com", "www.github.com"}
        valid_scheme = parsed_url.scheme in {"http", "https"}

        if not valid_scheme or not valid_domain:
            raise forms.ValidationError("Укажите ссылку на github.com")

        return github_url


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput,
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
    )
