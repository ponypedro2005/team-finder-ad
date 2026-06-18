import random
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

# Константы
AVATAR_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
    "#A8E6CF", "#DCEDC1", "#FFD3B6", "#FFAAA5",
    "#D4A5A5", "#9B59B6", "#3498DB", "#1ABC9C",
    "#2ECC71", "#F1C40F", "#E67E22", "#E74C3C",
    "#7F6A93", "#5F8A8B", "#8A7E66",
]
AVATAR_SIZE = 128


def get_color_from_string(string: str) -> str:
    """Выбирает цвет на основе строки (email или name)"""
    hash_value = hash(string)
    color_index = abs(hash_value) % len(AVATAR_COLORS)
    return AVATAR_COLORS[color_index]


def generate_avatar_file(name: str, email: str) -> ContentFile:
    """Генерирует файл аватарки с инициалами"""
    # Выбираем цвет на основе email
    color = get_color_from_string(email)
    
    # Создаем изображение
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color)
    draw = ImageDraw.Draw(image)
    
    # Получаем инициалы
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        initials = f"{name_parts[0][0]}{name_parts[1][0]}".upper()
    elif len(name_parts) == 1:
        initials = name_parts[0][0].upper()
    else:
        initials = "U"
    
    # Рисуем текст
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
    
    # Сохраняем в BytesIO
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    
    return ContentFile(
        buffer.getvalue(),
        name=f"avatar_{email}.png"
    )


def paginate_queryset(request, queryset, per_page=12):
    """Пагинация queryset"""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def normalize_phone_number(phone: str) -> str:
    """Нормализует номер телефона к формату +7XXXXXXXXXX"""
    # Удаляем все нецифровые символы
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
