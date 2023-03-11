from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Objective, Area, Metric, Activity
from strategy.models import StrategicAxis


class AreaModelTests(TestCase):
    def test_area_without_english_text_shows_that_text(self):
        """
        Objects without text in English are created normally and its string is this text
        """
        text = "Area"
        area = Area.objects.create(text=text)
        self.assertEqual(area.text, area.__str__())
        self.assertIsNone(area.text_en)

    def test_area_with_only_english_text_raises_a_validation_error(self):
        """
        When objects don't have the text field filled, the object is not created
        """
        text_en = "Area"

        area = Area.objects.create(text_en=text_en)

        try:
            area.clean()
        except ValidationError as e:
            self.assertTrue("You need to fill the text field" in e.message)

    def test_area_with_both_texts_shows_the_non_english_text(self):
        """
        Objects with both texts filled give preference to the non english (local)
        language
        """
        text = "Area"
        text_en = "Area_English"

        area = Area.objects.create(text=text, text_en=text_en)
        self.assertEqual(area.text, area.__str__())
        self.assertNotEqual(area.text_en, area.__str__())
        self.assertIsNotNone(area.text_en)
        self.assertIsNotNone(area.text)

    def test_create_area_without_any_text_raises_validation_error(self):
        """
        Objects without any text are not created and a validation error is raised
        """
        area = Area.objects.create()

        try:
            area.clean()
        except ValidationError as e:
            print(e.message)
            self.assertTrue("You need to fill the text field" in e.message)

    def test_create_area_with_text_is_indeed_created(self):
        """
        Objects with the proper parameters are created
        """
        number_of_areas_on_database_before_creation = Area.objects.count()
        text = "Test"
        text_en = "Test_English"
        area = Area.objects.create(text=text, text_en=text_en)
        number_of_areas_on_database_after_creation = Area.objects.count()
        self.assertIsNotNone(area.text)
        self.assertNotEqual(number_of_areas_on_database_before_creation,
                            number_of_areas_on_database_after_creation)

    def test_create_area_with_links_to_strategic_axis_fails_if_it_doesnt_exists(self):
        text = "Area"
        text_en = "Area_English"
        text1 = "Strategic_Axis"

        strategic_axis = StrategicAxis.objects.create(text=text1)
        area = Area.objects.create(text=text, text_en=text_en)
        area.related_axis.add(strategic_axis)
        area.save()

        self.assertEqual(Area.objects.count(), 1)
        self.assertEqual(StrategicAxis.objects.count(), 1)


class ObjectiveModelTests(TestCase):

    def test_objective_without_english_text_shows_that_text(self):
        """
        Objects without text in English are created normally and its string is this text
        """
        text = "Objective"
        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        objective = Objective.objects.create(text=text, area=area)
        self.assertEqual(objective.text, objective.__str__())
        self.assertIsNone(objective.text_en)

    def test_objective_with_only_english_text_raises_a_validation_error(self):
        """
        When objects don't have the text field filled, the object is not created
        """
        text_en = "Objective"
        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        objective = Objective.objects.create(text_en=text_en, area=area)

        try:
            objective.clean()
        except ValidationError as e:
            print(e.message)
            self.assertTrue("You need to fill the text field" in e.message)

    def test_objective_with_both_texts_shows_the_non_english_text(self):
        """
        Objects with both texts filled give preference to the non english (local)
        language
        """
        text = "Objective"
        text_en = "Objective_English"
        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        objective = Objective.objects.create(text=text, text_en=text_en, area=area)
        self.assertEqual(objective.text, objective.__str__())
        self.assertNotEqual(objective.text_en, objective.__str__())
        self.assertIsNotNone(objective.text_en)
        self.assertIsNotNone(objective.text)

    def test_create_objective_with_proper_parameters_is_indeed_created(self):
        """
        Objects creates with proper necessary parameters are indeed created
        """
        number_of_objectives_on_database_before_creation = Objective.objects.count()
        text = "Test"
        text_en = "Test_English"
        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        objective = Objective.objects.create(text=text, text_en=text_en, area=area)
        number_of_objectives_on_database_after_creation = Objective.objects.count()
        self.assertIsNotNone(objective.text)
        self.assertNotEqual(number_of_objectives_on_database_before_creation,
                            number_of_objectives_on_database_after_creation)


class ActivityModelTests(TestCase):

    def test_activity_without_english_text_shows_that_text(self):
        """
        Objects without text in English are created normally and its string is this text
        """
        text = "Activity"

        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        activity = Activity.objects.create(text=text, area=area)
        self.assertEqual(activity.text, activity.__str__())
        self.assertIsNone(activity.text_en)

    def test_activity_with_only_english_text_raises_a_validation_error(self):
        """
        When objects don't have the text field filled, the object is not created
        """
        text_en = "Activity"

        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        activity = Activity.objects.create(text_en=text_en, area=area)

        try:
            activity.clean()
        except ValidationError as e:
            print(e.message)
            self.assertTrue("You need to fill the text field" in e.message)

    def test_activity_with_both_texts_shows_the_non_english_text(self):
        """
        Objects with both texts filled give preference to the non english (local)
        language
        """
        text = "Activity"
        text_en = "Activity_English"

        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        activity = Activity.objects.create(text=text, text_en=text_en, area=area)
        self.assertEqual(activity.text, activity.__str__())
        self.assertNotEqual(activity.text_en, activity.__str__())
        self.assertIsNotNone(activity.text_en)
        self.assertIsNotNone(activity.text)


class MetricModelTests(TestCase):
    def test_metric_without_english_text_shows_that_text(self):
        """
        Objects without text in English are created normally and its string is this text
        """
        text = "Metric"

        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        activity = Activity.objects.create(text="Activity", area=area)
        metric = Metric.objects.create(text=text, activity=activity)

        self.assertEqual(metric.text, metric.__str__())
        self.assertIsNone(metric.text_en)

    def test_metric_with_only_english_text_raises_a_validation_error(self):
        """
        When objects don't have the text field filled, the object is not created
        """
        text_en = "Metric"

        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        activity = Activity.objects.create(text="Activity", area=area)
        metric = Metric.objects.create(text_en=text_en, activity=activity)

        try:
            metric.clean()
        except ValidationError as e:
            self.assertTrue("You need to fill the text field" in e.message)

    def test_metric_with_both_texts_shows_the_non_english_text(self):
        """
        Objects with both texts filled give preference to the non english (local)
        language
        """
        text = "Metric"
        text_en = "Metric_English"

        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        area = Area.objects.create(text="Area")
        area.related_axis.add(strategic_axis)
        area.save()
        activity = Activity.objects.create(text="Activity", area=area)
        metric = Metric.objects.create(text=text, text_en=text_en, activity=activity)
        self.assertEqual(metric.text, metric.__str__())
        self.assertNotEqual(metric.text_en, metric.__str__())
        self.assertIsNotNone(metric.text_en)
        self.assertIsNotNone(metric.text)
