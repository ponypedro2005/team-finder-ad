from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from constants import UserConstants
from utils import generate_avatar_file


class UserManager(models.Manager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        
        if 'name' not in extra_fields:
            extra_fields.setdefault('name', 'User')
        if 'surname' not in extra_fields:
            extra_fields.setdefault('surname', 'Unknown')
        if 'phone' not in extra_fields:
            extra_fields.setdefault('phone', '+70000000000')
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if 'name' not in extra_fields:
            extra_fields['name'] = 'Admin'
        if 'surname' not in extra_fields:
            extra_fields['surname'] = 'User'
        if 'phone' not in extra_fields:
            extra_fields['phone'] = '+70000000000'

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    name = models.CharField(
        max_length=UserConstants.NAME_MAX_LENGTH,
        verbose_name='Имя'
    )
    surname = models.CharField(
        max_length=UserConstants.SURNAME_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='default_avatar.png',
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=UserConstants.PHONE_MAX_LENGTH,
        verbose_name='Телефон'
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на GitHub'
    )
    about = models.TextField(
        max_length=UserConstants.ABOUT_MAX_LENGTH,
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Сотрудник'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации'
    )

    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True,
        verbose_name='Избранное'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar or self.avatar.name == 'default_avatar.png':
            self.avatar = generate_avatar_file(self.name, self.email)
        super().save(*args, **kwargs)
