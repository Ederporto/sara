import datetime
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from agenda.models import Event
from users.models import User, UserProfile, TeamArea


class EventModelTests(TestCase):
    def setUp(self):
        self.area_responsible = TeamArea.objects.create(text="Area Responsible", code="area_responsible")
        self.area_involved_1 = TeamArea.objects.create(text="Area Involved 1", code="area_involved_1")
        self.area_involved_2 = TeamArea.objects.create(text="Area Involved 2", code="area_involved_2")
        self.event = Event.objects.create(
            name="Test Event",
            initial_date=datetime.date(2023, 3, 24),
            end_date=datetime.date(2023, 3, 31),
            area_responsible=self.area_responsible,
        )

    def test_str_method_with_end_date_different_from_initial_date(self):
        correct_output = "Test Event (24/Mar - 31/Mar)"
        self.assertEqual(str(self.event), correct_output)

    def test_str_method_with_end_date_equal_from_initial_date(self):
        correct_output = "Test Event (24/Mar)"

        self.event.end_date = self.event.initial_date
        self.event.save()

        self.assertEqual(str(self.event), correct_output)

    def test_clean_method(self):
        event = Event.objects.create(
            name="Test Event 2",
            initial_date=datetime.date(2023, 3, 24),
            end_date=datetime.date(2023, 3, 31),
            area_responsible=self.area_responsible,
        )
        event.full_clean()

        with self.assertRaises(ValidationError):
            event.name = ""
            event.full_clean()


class EventViewTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpass"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user_profile = UserProfile.objects.filter(user=self.user).first()
        self.team_area = TeamArea.objects.create(text="Team Area", code="Code")
        self.name = "Setup"

        self.day = 19
        self.month = 4
        self.year = 2023

        self.event = Event.objects.create(name=self.name,
                                          initial_date=datetime.date.today(),
                                          end_date=datetime.date.today(),
                                          area_responsible=self.team_area)

    def test_show_calendar_for_logged_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('agenda:show_calendar'))
        self.assertRedirects(response, reverse('agenda:show_specific_calendar',
                                               kwargs={"year": datetime.datetime.now().year,
                                                       "month": datetime.datetime.now().month}))

    def test_show_calendar_for_non_logged_user_redirects_to_login_page(self):
        response = self.client.get(reverse('agenda:show_calendar'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('agenda:show_calendar')}")

    def test_show_specific_calendar_for_logged_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('agenda:show_specific_calendar',
                                           kwargs={"year": self.year, "month": self.month}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/calendar.html')

    def test_show_specific_calendar_for_non_logged_user_redirects_to_login_page(self):
        response = self.client.get(reverse('agenda:show_specific_calendar',
                                           kwargs={"year": self.year, "month": self.month}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('agenda:show_specific_calendar',kwargs={'year': self.year, 'month': self.month})}")

    def test_show_calendar_day_for_logged_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('agenda:show_calendar_day'))
        self.assertRedirects(response, reverse('agenda:show_specific_calendar_day',
                                               kwargs={"year": datetime.datetime.now().year,
                                                       "month": datetime.datetime.now().month,
                                                       "day": datetime.datetime.now().day}))

    def test_show_calendar_day_for_non_logged_user_redirects_to_login_page(self):
        response = self.client.get(reverse('agenda:show_calendar_day'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('agenda:show_calendar_day')}")

    def test_show_specific_calendar_day_for_logged_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('agenda:show_specific_calendar_day',
                                           kwargs={"year": self.year, "month": self.month, "day": self.day}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/calendar_day.html')

    def test_show_specific_calendar_day_for_non_logged_user_redirects_to_login_page(self):
        response = self.client.get(reverse('agenda:show_specific_calendar_day',
                                           kwargs={"year": self.year, "month": self.month, "day": self.day}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('agenda:show_specific_calendar_day', kwargs={'year': self.year, 'month': self.month, 'day': self.day})}")

    def test_add_event_get(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:create_event")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_add_event_post(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:create_event")
        data = {
            "name": "Title",
            "initial_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "area_responsible": self.team_area.pk
        }
        response = self.client.post(url, data=data)

        event = Event.objects.get(name=data["name"],
                                  initial_date=data["initial_date"],
                                  end_date=data["end_date"],
                                  area_responsible=data["area_responsible"])
        self.assertRedirects(response, reverse('agenda:list_events'))
        self.assertEqual(event.area_responsible, self.team_area)

    def test_add_event_post_with_invalid_parameters(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:create_event")
        data = {
            "initial_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "area_responsible": self.team_area.pk,
            "name": "",
        }
        self.client.post(url, data=data)
        self.assertFalse(Event.objects.filter(name="").exists())

    def test_list_events(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:list_events")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_delete_event_get(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:delete_event", kwargs={"event_id": self.event.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/delete_event.html')

    def test_delete_event_post(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:delete_event", kwargs={"event_id": self.event.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())

    def test_update_event_get(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:edit_event", kwargs={"event_id": self.event.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/update_event.html')

    def test_update_event_post(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:edit_event", kwargs={"event_id": self.event.pk})

        data = {
            "name": "New title",
            "initial_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "area_responsible": self.team_area.pk
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(name="New title").exists())
        self.assertFalse(Event.objects.filter(name=self.name).exists())

    def test_update_event_post_with_invalid_parameters(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("agenda:edit_event", kwargs={"event_id": self.event.pk})

        data = {
            "name": "",
            "initial_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "area_responsible": self.team_area.pk
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(name="").exists())
        self.assertTrue(Event.objects.filter(name=self.name).exists())
