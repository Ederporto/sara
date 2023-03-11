from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import StrategicAxis, Direction


class DirectionModelTests(TestCase):
    def test_direction_without_english_text_shows_that_text(self):
        """
        Objects without text in English are created normally and its string is this text
        """
        text = "Direction"
        strategic_axis, created = StrategicAxis.objects.get_or_create(text="StrategicAxis")

        direction = Direction.objects.create(text=text, strategic_axis=strategic_axis)

        direction.clean()
        self.assertEqual(direction.text, direction.__str__())
        self.assertIsNone(direction.text_en)

    def test_direction_with_only_english_text_raises_validation_error(self):
        """
        When objects don't have the text field filled, the object is not created
        """
        text_en = "Direction_English"
        strategic_axis, created = StrategicAxis.objects.get_or_create(text="StrategicAxis")

        direction = Direction.objects.create(text_en=text_en, strategic_axis=strategic_axis)

        try:
            direction.clean()
        except ValidationError as e:
            self.assertTrue("You need to fill the text field" in e.message)

    def test_direction_with_both_texts_shows_the_non_english_text(self):
        """
        Objects with both texts filled give preference to the non english (local)
        language
        """
        text = "Direction"
        text_en = "Direction_English"
        strategic_axis, created = StrategicAxis.objects.get_or_create(text="StrategicAxis")

        direction = Direction.objects.create(text=text, text_en=text_en, strategic_axis=strategic_axis)
        direction.clean()

        self.assertEqual(direction.text, direction.__str__())
        self.assertNotEqual(direction.text_en, direction.__str__())

    def test_create_direction_without_any_text_raises_validation_error(self):
        """
        Objects without any text are not created and a validation error is raised
        """
        strategic_axis, created = StrategicAxis.objects.get_or_create(text="StrategicAxis")
        direction = Direction.objects.create(strategic_axis=strategic_axis)

        try:
            direction.clean()
        except ValidationError as e:
            self.assertTrue('You need to fill the text field' in e.message)

    def test_create_direction_with_text_is_indeed_created(self):
        """
        Objects with the proper parameters are created
        """
        number_of_directions_on_database_before_creation = Direction.objects.count()
        text = "Direction"
        text_en = "Direction_English"
        strategic_axis, created = StrategicAxis.objects.get_or_create(text="StrategicAxis")
        direction = Direction.objects.create(text=text, text_en=text_en, strategic_axis=strategic_axis)
        direction.clean()

        number_of_directions_on_database_after_creation = Direction.objects.count()
        self.assertNotEqual(number_of_directions_on_database_before_creation,
                            number_of_directions_on_database_after_creation)


class StrategicAxisModelTests(TestCase):
    def test_strategic_axis_without_english_text_shows_that_text(self):
        """
        Objects without text in English are created normally and its string is this text
        """
        text = "Strategic Axis"
        strategic_axis = StrategicAxis.objects.create(text=text)
        self.assertEqual(strategic_axis.text, strategic_axis.__str__())
        self.assertIsNone(strategic_axis.text_en)

    def test_strategic_axis_with_only_english_text_raises_validation_error(self):
        """
        When objects do not have the text field filled, the object is not created
        """
        text_en = "Strategic Axis"
        strategic_axis = StrategicAxis.objects.create(text_en=text_en)
        self.assertNotEqual(strategic_axis.text_en, strategic_axis.__str__())
        self.assertEqual(strategic_axis.text, '')

    def test_strategic_axis_with_both_texts_shows_the_non_english_text(self):
        """
        Objects with both texts filled give preference to the non english (local)
        language
        """
        text = "Strategic Axis"
        text_en = "Strategic Axis_English"
        strategic_axis = StrategicAxis.objects.create(text=text, text_en=text_en)

        self.assertEqual(strategic_axis.text, strategic_axis.__str__())
        self.assertNotEqual(strategic_axis.text_en, strategic_axis.__str__())
        self.assertIsNotNone(strategic_axis.text_en)
        self.assertIsNotNone(strategic_axis.text)

    def test_create_strategic_axis_without_any_text_raises_validation_error(self):
        """
        Objects without any text are not created and a validation error is raised
        """
        strategic_axis = StrategicAxis.objects.create()

        try:
            strategic_axis.clean()
        except ValidationError as e:
            print(e.message)
            self.assertTrue('You need to fill the text field' in e.message)

    def test_create_strategic_axis_with_text_is_indeed_created(self):
        """
        Objects with the proper parameters are created
        """
        number_of_strategic_axiss_on_database_before_creation = StrategicAxis.objects.count()
        text = "Test"
        strategic_axis = StrategicAxis.objects.create(text=text)
        number_of_strategic_axiss_on_database_after_creation = StrategicAxis.objects.count()
        self.assertIsNotNone(strategic_axis.text)
        self.assertNotEqual(number_of_strategic_axiss_on_database_before_creation,
                            number_of_strategic_axiss_on_database_after_creation)
