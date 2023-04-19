from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import RestrictedError
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.messages import get_messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Bug, Observation
from users.models import User, UserProfile


class BugModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="username",
            email="email@email.com",
            first_name="First Name",
            last_name="Last Name")

        self.title = "Test Bug"
        self.description = "Test Description"

        self.reporter = UserProfile.objects.filter(user=self.user).first()
        self.bug = Bug.objects.create(
            title=self.title,
            description=self.description,
            reporter=self.reporter,
        )

    def test_str_method_returns_bug_title(self):
        bug = Bug.objects.create(
            title=self.title,
            description=self.description,
            reporter=self.reporter,
        )
        self.assertEqual(str(bug), self.title)

    def test_create_bug_without_description_fails(self):
        with self.assertRaises(ValidationError):
            bug = Bug.objects.create(title=self.title, reporter=self.reporter)
            bug.full_clean()

    def test_create_bug_without_title_fails(self):
        with self.assertRaises(ValidationError):
            bug = Bug.objects.create(description=self.description, reporter=self.reporter)
            bug.full_clean()

    def test_create_bug_without_reporter_fails(self):
        with self.assertRaises(IntegrityError):
            bug = Bug.objects.create(title=self.title, description=self.description)
            bug.full_clean()

    def test_create_bug_with_minimal_requirements_succeeds(self):
        bug = Bug.objects.create(title=self.title, description=self.description, reporter=self.reporter)
        bug.full_clean()
        self.assertTrue(Bug.objects.filter(pk=bug.pk).exists())

    def test_trying_to_delete_a_user_with_bugs_associated_fails(self):
        with self.assertRaises(RestrictedError):
            self.user.delete()


class BugViewsTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpass"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user_profile = UserProfile.objects.filter(user=self.user).first()
        self.title = "Title"
        self.description = "Description"
        self.type_of_bug = Bug.BugType.ERROR
        self.bug = Bug.objects.create(title=self.title,
                                      description=self.description,
                                      reporter=self.user_profile,
                                      type_of_bug=self.type_of_bug)

    def test_add_bug_view_get(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("bug:create_bug")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_add_bug_view_post(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("bug:create_bug")
        data = {
            "title": "Title2",
            "description": "Description2",
            "type_of_bug": Bug.BugType.ERROR,
            "status": Bug.Status.TODO
        }
        response = self.client.post(url, data=data)

        bug = Bug.objects.get(title=data["title"],
                              description=data["description"],
                              type_of_bug=data["type_of_bug"],
                              status=data["status"])
        self.assertRedirects(response, reverse('bug:detail_bug', kwargs={'bug_id': bug.pk}))
        self.assertEqual(bug.reporter.user, self.user)

    def test_add_bug_view_post_fails_with_invalid_parameters(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("bug:create_bug")
        data = {
            "title": "",
            "description": "Description2",
            "type_of_bug": Bug.BugType.ERROR,
            "status": Bug.Status.TODO
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong!")

    def test_list_bugs_view(self):
        url = reverse("bug:list_bugs")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.bug, response.context["dataset"])

    def test_detail_bug_view(self):
        url = reverse("bug:detail_bug", args=[self.bug.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["data"], self.bug)

    def test_update_bug_view(self):
        url = reverse("bug:edit_bug", args=[self.bug.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = {
            "title": "Testess",
            "status": Bug.Status.DONE,
            "description": "This is an updated test bug.",
            "type_of_bug": Bug.BugType.ERROR,
            "reporter": self.user
        }

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse("bug:detail_bug", args=[self.bug.id]))

    def test_update_bug_view_fails_with_invalid_parameters(self):
        url = reverse("bug:edit_bug", args=[self.bug.id])

        data = {
            "title": "",
            "status": Bug.Status.DONE,
            "description": "This is an updated test bug.",
            "type_of_bug": Bug.BugType.ERROR,
            "reporter": self.user
        }

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong!")

    def test_add_observation_view_get(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("bug:add_obs", args=[self.bug.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_add_observation_view_post(self):
        url = reverse("bug:add_obs", args=[self.bug.id])
        data = {"observation": "Observation"}

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse("bug:detail_bug", args=[self.bug.id]))

    def test_add_observation_view_post_fails_with_invalid_parameters(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("bug:add_obs", args=[self.bug.id])
        data = {"observation": ""}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong!")

    def test_update_observation_view(self):
        url = reverse("bug:edit_obs", args=[self.bug.id])
        obs = Observation.objects.create(bug_report=self.bug,
                                         observation="Observation")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {"observation": "Observation2"}

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse("bug:detail_bug", args=[self.bug.id]))

    def test_update_observation_view_fails_with_invalid_parameters(self):
        url = reverse("bug:edit_obs", args=[self.bug.id])
        Observation.objects.create(bug_report=self.bug,
                                   observation="Observation")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {"observation": ""}

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong!")
