from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()


class UserViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            name="Test",
            surname="User",
            phone="+79990000011",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            email="other@test.com",
            name="Other",
            surname="User",
            phone="+79990000012",
            password="testpass123",
        )
        self.project = Project.objects.create(
            name="User project",
            description="Desc",
            owner=self.user,
            status=Project.STATUS_OPEN,
        )
        self.project.participants.add(self.user)

        self.client = Client()

    def test_register_page_available(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_page_available(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_detail_page_available(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"user_id": self.user.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_list_page_available(self):
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse("users:edit_profile"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_change_password_requires_login(self):
        response = self.client.get(reverse("users:change_password"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_filter_favorite_authors(self):
        self.other_user.favorites.add(self.project)
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("users:list"),
            {"filter": "favorite_authors"},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_filter_participated_authors(self):
        self.project.participants.add(self.other_user)
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("users:list"),
            {"filter": "participated_authors"},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
