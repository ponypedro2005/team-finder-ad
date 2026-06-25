# constants.py

# Константы для моделей пользователей
class UserConstants:
    NAME_MAX_LENGTH = 124
    SURNAME_MAX_LENGTH = 124
    PHONE_MAX_LENGTH = 12
    ABOUT_MAX_LENGTH = 256
    AVATAR_SIZE = 128

# Константы для моделей проектов
class ProjectConstants:
    NAME_MAX_LENGTH = 200
    # STATUS_MAX_LENGTH будет вычисляться динамически

# Константы для пагинации
PAGINATION = {
    "USERS_PER_PAGE": 12,
    "PROJECTS_PER_PAGE": 12,
}

# Цвета для аватарок
AVATAR_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
    "#A8E6CF", "#DCEDC1", "#FFD3B6", "#FFAAA5",
    "#D4A5A5", "#9B59B6", "#3498DB", "#1ABC9C",
    "#2ECC71", "#F1C40F", "#E67E22", "#E74C3C",
    "#7F6A93", "#5F8A8B", "#8A7E66",
]

# Фильтры для страницы пользователей
class UserFilters:
    FAVORITE_AUTHORS = "favorite_authors"
    PARTICIPATED_AUTHORS = "participated_authors"
    LIKED_MY_PROJECTS = "liked_my_projects"
    MY_PROJECT_PARTICIPANTS = "my_project_participants"
