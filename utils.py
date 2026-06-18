import hashlib
import re
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

PHONE_PATTERN = re.compile(r"^(8\d{10}|\+7\d{10})$")

AVATAR_COLORS = [
    "#6B8E73",
    "#7C90A0",
    "#8D7B68",
    "#7F6A93",
    "#5F8A8B",
    "#8A7E66",
]


def paginate_queryset(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def normalize_phone_number(raw_phone: str) -> str:
    value = (raw_phone or "").strip()
    return f"+7{value[-10:]}"


def pick_avatar_background(seed: str) -> str:
    source = (seed or "user").encode("utf-8")
    color_index = int(hashlib.md5(source).hexdigest(), 16) % len(AVATAR_COLORS)
    return AVATAR_COLORS[color_index]


def build_avatar_file(name: str, email: str) -> ContentFile:
    image_size = 128
    bg_color = pick_avatar_background(email or name)

    avatar_image = Image.new("RGB", (image_size, image_size), bg_color)
    canvas = ImageDraw.Draw(avatar_image)

    first_letter = (name[:1] if name else "U").upper()

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 72)
    except OSError:
        font = ImageFont.load_default()

    text_box = canvas.textbbox((0, 0), first_letter, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]

    text_x = (image_size - text_width) / 2
    text_y = (image_size - text_height) / 2

    canvas.text((text_x, text_y), first_letter, fill="white", font=font)

    binary_stream = BytesIO()
    avatar_image.save(binary_stream, format="PNG")
    file_name = f"avatar_{email.replace('@', '_').replace('.', '_')}.png"

    return ContentFile(binary_stream.getvalue(), name=file_name)
