import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from .models import Event
from users.models import TeamArea


class EventModelTests(TestCase):
    def test_calendar_event_without_title_raises_error(self):
        """
        Objects without text are not created
        """
        ini_date = datetime.datetime.now()
        end_date = datetime.datetime.now()
        area_responsible = TeamArea.objects.create(text="Area Responsible")
        calendar = Event.objects.create(initial_date=ini_date, end_date=end_date, area_responsible=area_responsible)

        try:
            calendar.clean()
        except ValidationError as e:
            self.assertTrue("Every event needs a name, a date of beginning and ending" in e.message)

    def test_calendar_event_without_ini_date_raises_error(self):
        """
        Objects without text are not created
        """
        text = "Calendar Event"
        end_date = datetime.datetime.now()
        area_responsible = TeamArea.objects.create(text="Area Responsible")

        try:
            Event.objects.create(text=text, end_date=end_date, area_responsible=area_responsible)
        except IntegrityError as e:
            self.assertTrue("NOT NULL constraint failed: agenda_event.initial_date" in str(e))

    def test_calendar_event_without_end_date_raises_error(self):
        """
        Objects without text are not created
        """
        text = "Calendar Event"
        ini_date = datetime.datetime.now()
        area_responsible = TeamArea.objects.create(text="Area Responsible")

        try:
            Event.objects.create(text=text, initial_date=ini_date, area_responsible=area_responsible)
        except IntegrityError as e:
            self.assertTrue("NOT NULL constraint failed: agenda_event.end_date" in str(e))

    def test_calendar_event_with_proper_arguments_returns_formatted_string(self):
        text = "Calendar Event"
        ini_date = datetime.datetime.now()
        end_date = datetime.datetime.now()
        area_responsible = TeamArea.objects.create(text="Area Responsible")
        calendar = Event.objects.create(text=text, initial_date=ini_date, end_date=end_date,
                                        area_responsible=area_responsible)

        self.assertEqual(text + "(" + ini_date.strftime("%d/%b") + " - " + end_date.strftime("%d/%b") + ")",
                         calendar.__str__())

    def test_delete_team_area_deletes_events_associated_with_it(self):
        text = "Calendar Event"
        ini_date = datetime.datetime.now()
        end_date = datetime.datetime.now()
        area_responsible = TeamArea.objects.create(text="Area Responsible")
        calendar = Event.objects.create(text=text, initial_date=ini_date, end_date=end_date,
                                        area_responsible=area_responsible)
        calendar.clean()
        calendar.save()

        self.assertEqual(TeamArea.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(calendar.area_responsible.text, TeamArea.objects.first().text)

        TeamArea.objects.get(pk=area_responsible.pk).delete()
        self.assertEqual(TeamArea.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
