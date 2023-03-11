from django.test import TestCase
from .models import TeamArea
from django.core.exceptions import ValidationError


class TeamAreaModelTests(TestCase):
    def test_team_area_without_english_text_shows_that_text(self):
        """
        Objects without text in English are created normally and its string is this text
        """
        text = "Team Area"

        team_area = TeamArea.objects.create(text=text)

        team_area.clean()
        self.assertEqual(team_area.text, team_area.__str__())
        self.assertIsNone(team_area.text_en)

    def test_team_area_with_only_english_text_raises_validation_error(self):
        """
        When objects don't have the text field filled, the object is not created
        """
        text_en = "Team Area_English"

        team_area = TeamArea.objects.create(text_en=text_en)

        try:
            team_area.clean()
        except ValidationError as e:
            self.assertTrue("You need to fill the text field" in e.message)

    def test_team_area_with_both_texts_shows_the_non_english_text(self):
        """
        Objects with both texts filled give preference to the non english (local)
        language
        """
        text = "Team Area"
        text_en = "Team Area_English"

        team_area = TeamArea.objects.create(text=text, text_en=text_en)
        team_area.clean()

        self.assertEqual(team_area.text, team_area.__str__())
        self.assertNotEqual(team_area.text_en, team_area.__str__())

    def test_create_team_area_without_any_text_raises_validation_error(self):
        """
        Objects without any text are not created and a validation error is raised
        """
        team_area = TeamArea.objects.create()

        try:
            team_area.clean()
        except ValidationError as e:
            self.assertTrue('You need to fill the text field' in e.message)

    def test_create_team_area_with_text_is_indeed_created(self):
        """
        Objects with the proper parameters are created
        """
        number_of_team_area_on_database_before_creation = TeamArea.objects.count()
        text = "Team Area"
        text_en = "Team Area_English"
        team_area = TeamArea.objects.create(text=text, text_en=text_en)
        team_area.clean()

        number_of_team_area_on_database_after_creation = TeamArea.objects.count()
        self.assertNotEqual(number_of_team_area_on_database_before_creation,
                            number_of_team_area_on_database_after_creation)
