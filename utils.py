from urllib.parse import urlparse

from django import forms
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

from constants import AVATAR_COLORS, PAGINATION, UserConstants

# Константы из constants.py
AVATAR_SIZE = UserConstants.AVATAR_SIZE


def get_color_from_string(string: str) -> str:
    """Выбирает цвет на основе строки (email или name)"""
    hash_value = hash(string)
    color_index = abs(hash_value) % len(AVATAR_COLORS)
    return AVATAR_COLORS[color_index]


def generate_avatar_file(name: str, email: str) -> ContentFile:
    """Генерирует файл аватарки с инициалами"""
    color = get_color_from_string(email)
    
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color)
    draw = ImageDraw.Draw(image)
    
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        initials = f"{name_parts[0][0]}{name_parts[1][0]}".upper()
    elif len(name_parts) == 1:
        initials = name_parts[0][0].upper()
    else:
        initials = "U"
    
    try:
        font = ImageFont.truetype("arial.ttf", int(AVATAR_SIZE * 0.5))
    except:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (AVATAR_SIZE - text_width) // 2
    y = (AVATAR_SIZE - text_height) // 2
    
    draw.text((x, y), initials, fill="white", font=font)
    
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    
    return ContentFile(
        buffer.getvalue(),
        name=f"avatar_{email}.png"
    )


def paginate_queryset(request, queryset, per_page=None):
    """Пагинация queryset"""
    if per_page is None:
        per_page = PAGINATION.get("USERS_PER_PAGE", 12)
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def normalize_phone_number(phone: str) -> str:
    """Нормализует номер телефона к формату +7XXXXXXXXXX"""
    phone = ''.join(filter(str.isdigit, phone))
    
    if len(phone) == 11 and phone.startswith('8'):
        return '+7' + phone[1:]
    elif len(phone) == 11 and phone.startswith('7'):
        return '+7' + phone[1:]
    elif len(phone) == 12 and phone.startswith('7'):
        return '+7' + phone[1:]
    elif len(phone) == 12 and phone.startswith('+7'):
        return '+7' + phone[2:]
    else:
        raise forms.ValidationError(
            "Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )
    
    return phone


def validate_github_url(github_url: str) -> str:
    """Валидация URL GitHub"""
    if not github_url:
        return github_url
    
    parsed_url = urlparse(github_url)
    domain = parsed_url.netloc.lower()
    valid_domain = domain in {"github.com", "www.github.com"}
    valid_scheme = parsed_url.scheme in {"http", "https"}
    
    if not valid_scheme or not valid_domain:
        raise forms.ValidationError("Укажите ссылку на github.com")
    
    return github_url
