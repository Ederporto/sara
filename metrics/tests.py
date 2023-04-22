from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from .models import Objective, Area, Metric, Activity
from strategy.models import StrategicAxis
from django.urls import reverse


class AreaModelTests(TestCase):
    def setUp(self):
        self.axis = StrategicAxis.objects.create(text="Strategic Axis")
        self.area = Area.objects.create(text="Area")

    def test_area_str_method_returns_area_text(self):
        self.assertEqual(str(self.area), 'Area')

    def test_area_can_have_related_axes(self):
        self.area.related_axis.add(self.axis)
        self.assertIn(self.axis, self.area.related_axis.all())

    def test_area_text_cannot_be_empty(self):
        with self.assertRaises(ValidationError):
            empty_area = Area(text="")
            empty_area.full_clean()


class ObjectiveModelTests(TestCase):
    def setUp(self):
        self.area = Area.objects.create(text='Area')
        self.obj = Objective.objects.create(text='Objective', area=self.area)

    def test_objective_str_returns_objective_text(self):
        self.assertEqual(str(self.obj), 'Objective')

    def test_objective_related_name_on_area_returns_objectives(self):
        self.assertIn(self.obj, self.area.objectives.all())

    def test_objective_cascade_deletes_with_area(self):
        self.area.delete()
        self.assertFalse(Objective.objects.filter(pk=self.obj.pk).exists())

    def test_objective_text_cannot_be_empty(self):
        with self.assertRaises(ValidationError):
            empty_obj = Objective(text="", area=self.area)
            empty_obj.full_clean()


class ActivityModelTests(TestCase):
    def setUp(self):
        self.area = Area.objects.create(text="Area")
        self.activity = Activity.objects.create(text="Activity", code="A1", area=self.area)

    def test_activity_str_returns_text(self):
        self.assertEqual(str(self.activity), "Activity")

    def test_activity_related_name_on_area_returns_activities(self):
        self.assertIn(self.activity, self.area.activities.all())

    def test_activity_text_cannot_be_empty(self):
        with self.assertRaises(ValidationError):
            empty_activity = Activity(text="", area=self.area)
            empty_activity.full_clean()


class MetricModelTests(TestCase):
    def setUp(cls):
        cls.area = Area.objects.create(text="Area")
        cls.activity = Activity.objects.create(text="Activity", area=cls.area)
        cls.metric = Metric.objects.create(text="Metric", activity=cls.activity)

    def test_metric_str_returns_metrics_text(self):
        self.assertEqual(str(self.metric), "Metric")

    def test_metric_instance_can_have_empty_text(self):
        with self.assertRaises(ValidationError):
            metric = Metric.objects.create(text="", activity=self.activity)
            metric.full_clean()

    def test_metric_instance_must_have_a_non_empty_text(self):
        with self.assertRaises(ValidationError):
            metric = Metric.objects.create(activity=self.activity)
            metric.full_clean()

    def test_metric_instance_must_have_an_activity_associated(self):
        with self.assertRaises(IntegrityError):
            Metric.objects.create(text="Metric2")

    def test_metric_instance_with_required_parameters_is_created(self):
        metric = Metric.objects.create(text="Metric3", activity=self.activity)
        metric.full_clean()


class MetricViewsTests(TestCase):
    def test_index_view(self):
        self.index_url = reverse("metrics:index")
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "metrics/home.html")

    def test_about_view(self):
        self.index_url = reverse("metrics:about")
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "metrics/about.html")

    def test_show_activities_plan_view(self):
        area = Area.objects.create(text="Area")
        activity = Activity.objects.create(text="Activity", area=area)
        url = reverse("metrics:show_activities")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "metrics/activities_plan.html")
        self.assertContains(response, "Activity")
        self.assertContains(response, "Area")
