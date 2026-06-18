from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@test.com",
            name="Owner",
            surname="User",
            phone="+79990000001",
            password="testpass123",
        )
        self.participant = User.objects.create_user(
            email="participant@test.com",
            name="Participant",
            surname="User",
            phone="+79990000002",
            password="testpass123",
        )
        self.project = Project.objects.create(
            name="Test project",
            description="Description",
            owner=self.owner,
            status=Project.STATUS_OPEN,
        )
        self.project.participants.add(self.owner)
        self.client = Client()

    def test_project_list_page_available(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "projects/project_list.html")

    def test_project_detail_page_available(self):
        response = self.client.get(
            reverse("projects:detail", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "projects/project-details.html")

    def test_create_project_sets_owner_and_participant(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create_project"),
            data={
                "name": "New project",
                "description": "New description",
                "github_url": "",
                "status": Project.STATUS_OPEN,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        created_project = Project.objects.get(name="New project")
        self.assertEqual(created_project.owner, self.owner)
        self.assertTrue(created_project.participants.filter(id=self.owner.id).exists())

    def test_toggle_participation(self):
        self.client.force_login(self.participant)
        response = self.client.post(
            reverse(
                "projects:toggle_participate", kwargs={"project_id": self.project.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            self.project.participants.filter(id=self.participant.id).exists()
        )

    def test_complete_project_by_owner(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:complete_project", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_toggle_favorite(self):
        self.client.force_login(self.participant)
        response = self.client.post(
            reverse("projects:toggle_favorite", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.participant.favorites.filter(id=self.project.id).exists())
