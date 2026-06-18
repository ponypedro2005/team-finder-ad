from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
from django.core.files.base import ContentFile

class CustomUserManager(models.Manager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        
        # Устанавливаем значения по умолчанию для обязательных полей, если они не переданы
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
        
        # Убедимся, что обязательные поля заполнены
        if 'name' not in extra_fields:
            extra_fields['name'] = 'Admin'
        if 'surname' not in extra_fields:
            extra_fields['surname'] = 'User'
        if 'phone' not in extra_fields:
            extra_fields['phone'] = '+70000000000'

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('first name'), max_length=124)
    surname = models.CharField(_('last name'), max_length=124)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', default='default_avatar.png')
    phone = models.CharField(_('phone number'), max_length=12, default='+70000000000')
    github_url = models.URLField(_('GitHub URL'), blank=True, null=True)
    about = models.TextField(_('about'), max_length=256, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    favorites = models.ManyToManyField('projects.Project', related_name='interested_users', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.name} {self.surname}"

    def natural_key(self):
        return (self.email,)

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            avatar_content = self.generate_avatar()
            self.avatar.save(f'avatar_{self.email}.png', avatar_content, save=False)
        super().save(*args, **kwargs)

    def generate_avatar(self):
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
        
        size = 200
        image = Image.new('RGB', (size, size), random.choice(colors))
        draw = ImageDraw.Draw(image)
        
        initials = f"{self.name[0]}{self.surname[0]}".upper()
        
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), initials, fill='white', font=font)
        
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        
        return ContentFile(buffer.getvalue(), name=f'avatar_{self.email}.png')
