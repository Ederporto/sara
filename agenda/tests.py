import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Event
from users.models import TeamArea


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
