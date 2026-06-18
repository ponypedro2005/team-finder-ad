from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Создание тестовых юзеров и проектов"

    def handle(self, *args, **options):
        password = "6767676767"

        user_1, created_1 = User.objects.get_or_create(
            email="sergey1@example.com",
            defaults={
                "name": "Сергио",
                "surname": "Батькович",
                "phone": "+79990000001",
                "about": "По жизни бродяга, по факту стиляга",
                "github_url": "https://github.com/sergey1",
            },
        )
        if created_1:
            user_1.set_password(password)
            user_1.save()

        user_2, created_2 = User.objects.get_or_create(
            email="sergey2@example.com",
            defaults={
                "name": "Сереборкин",
                "surname": "Матье",
                "phone": "+79990000002",
                "about": "Дал, дал, ушел",
                "github_url": "https://github.com/sergey2",
            },
        )
        if created_2:
            user_2.set_password(password)
            user_2.save()

        user_3, created_3 = User.objects.get_or_create(
            email="sergey3@example.com",
            defaults={
                "name": "Серафим",
                "surname": "Узкоглазов",
                "phone": "+79990000003",
                "about": "Широко гляжу",
                "github_url": "https://github.com/sergey3",
            },
        )
        if created_3:
            user_3.set_password(password)
            user_3.save()

        project_1, _ = Project.objects.get_or_create(
            name="ozontech-seq-ui",
            defaults={
                "description": "backend UI для анализа, просмотра и агрегирования логами",
                "owner": user_1,
                "github_url": "https://github.com/ozontech/seq-ui",
                "status": Project.STATUS_OPEN,
            },
        )
        project_1.participants.add(user_1, user_2)

        project_2, _ = Project.objects.get_or_create(
            name="ozontech-file.d",
            defaults={
                "description": "уникальный коннектор",
                "owner": user_2,
                "github_url": "https://github.com/ozontech/file.d",
                "status": Project.STATUS_OPEN,
            },
        )
        project_2.participants.add(user_2, user_3)

        project_3, _ = Project.objects.get_or_create(
            name="ozontech-seq-db",
            defaults={
                "description": "Просто хранилище логов",
                "owner": user_3,
                "github_url": "https://github.com/ozontech/seq-db",
                "status": Project.STATUS_OPEN,
            },
        )
        project_3.participants.add(user_3)

        user_2.favorites.add(project_1)
        user_3.favorites.add(project_1, project_2)

        self.stdout.write("Пользователи:")
        self.stdout.write("  sergey1@example.com / 6767676767")
        self.stdout.write("  sergey2@example.com / 6767676767")
        self.stdout.write("  sergey3@example.com / 6767676767")
