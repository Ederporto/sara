from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models import RestrictedError
from django.contrib.auth.models import Group
from django.contrib.auth.admin import User
from .models import TeamArea, Position, UserProfile
from agenda.models import Event
import datetime


class TeamAreaModelTests(TestCase):
    def setUp(self):
        self.text = "Team Area"
        self.code = "team_area"
        self.team_area = TeamArea.objects.create(text=self.text, code=self.code)

    def test_str_method(self):
        self.assertEqual(str(self.team_area), self.text)

    def test_clean_method(self):
        team_area2 = TeamArea.objects.create(text="Team Area 2", code="team_area_2")
        team_area2.full_clean()

        with self.assertRaises(ValidationError):
            team_area2.text = ""
            team_area2.full_clean()

        with self.assertRaises(ValidationError):
            team_area2.text = self.text
            team_area2.code = ""
            team_area2.full_clean()

    def test_trying_to_delete_team_area_that_are_responsible_for_events_fails(self):
        Event.objects.create(
            name="Test Event",
            initial_date=datetime.date(2023, 3, 24),
            end_date=datetime.date(2023, 3, 31),
            area_responsible=self.team_area,
        )

        with self.assertRaises(RestrictedError):
            self.team_area.delete()

    def test_trying_to_delete_team_area_that_are_not_responsible_for_events_succeds(self):
        team_area2 = TeamArea.objects.create(text="Team Area 2", code="team_area_2")

        Event.objects.create(
            name="Test Event",
            initial_date=datetime.date(2023, 3, 24),
            end_date=datetime.date(2023, 3, 31),
            area_responsible=self.team_area,
        )

        team_area2.delete()
        self.assertEqual(TeamArea.objects.count(), 1)


class PositionModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="Group_name")
        self.text = "Position"
        self.area_associated = TeamArea.objects.create(text="Team Area", code="team_area")

        self.position = Position.objects.create(text=self.text,
                                                type=self.group,
                                                area_associated=self.area_associated)

    def test_str_method(self):
        self.assertEqual(str(self.position), self.text)

    def test_deleting_team_area_deletes_position_as_well(self):
        self.assertEqual(Position.objects.count(), 1)
        self.area_associated.delete()
        self.assertEqual(Position.objects.count(), 0)

    def test_deleting_group_deletes_position_as_well(self):
        self.assertEqual(Position.objects.count(), 1)
        self.group.delete()
        self.assertEqual(Position.objects.count(), 0)


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.first_name = "First Name"
        self.user = User.objects.create(
            username="username",
            email="email@email.com",
            first_name=self.first_name,
            last_name="Last Name")
        self.user_profile = UserProfile.objects.filter(user=self.user).first()

    def test_str_method_returns_first_name_if_there_is_no_professional_wiki_handle(self):
        self.assertTrue(str(self.user_profile), self.first_name)

    def test_str_method_returns_professional_wiki_handle_if_present(self):
        professional_wiki_handle = "Professional Wiki handle"
        self.user_profile.professional_wiki_handle = professional_wiki_handle
        self.assertTrue(str(self.user_profile), professional_wiki_handle)

    def test_clean_method(self):
        with self.assertRaises(ValidationError):
            user = User.objects.create(username="username2",
                                       email="email2@email.com",
                                       first_name="First Name 2",
                                       last_name="Last Name 2")
            user_profile = UserProfile.objects.filter(user=user).first()
            user_profile.full_clean()
