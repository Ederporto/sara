from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from .models import Objective, Area, Metric, Activity, Project
from report.models import Report, Editor
from users.models import User, UserProfile, TeamArea
from strategy.models import StrategicAxis
from .views import get_metrics_and_aggregate_per_project, get_aggregated_metrics_data, get_aggregated_metrics_data_done, get_activities, get_chart_data, get_chart_data_many_to_many
from django.urls import reverse
from django.contrib.auth.models import Permission
from datetime import datetime, timedelta
from metrics.templatetags.metricstags import categorize, perc


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


class ProjectModelTests(TestCase):
    def setUp(self):
        self.text = "text"
        self.status = True
        self.project = Project.objects.create(text=self.text, status=self.status)

    def test_project_str_returns_text(self):
        self.assertEqual(str(self.project), self.text)

    def test_project_text_cant_be_empty(self):
        with self.assertRaises(ValidationError):
            empty_project = Project(text="")
            empty_project.full_clean()


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
    def setUp(self):
        self.username = "testuser"
        self.password = "testpass"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.view_metrics_permission = Permission.objects.get(codename="view_metric")
        self.user.user_permissions.add(self.view_metrics_permission)

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
        project = Project.objects.create(text="Plano de atividades")
        area = Area.objects.create(text="Area")
        area.project.add(project)
        Activity.objects.create(text="Activity", area=area)
        url = reverse("metrics:show_activities")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "metrics/activities_plan.html")
        self.assertContains(response, "Activity")
        self.assertContains(response, "Area")

    def test_show_metrics_is_only_visible_for_users_with_permission(self):
        self.user.user_permissions.remove(self.view_metrics_permission)
        self.client.login(username=self.username, password=self.password)
        url = reverse("metrics:metrics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('metrics:metrics')}")

    def test_show_metrics_get_is_shown(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("metrics:metrics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "metrics/list_metrics.html")

    def test_show_metrics_per_project(self):
        self.client.login(username=self.username, password=self.password)
        project = Project.objects.create(text="Project")
        url = reverse("metrics:per_project")

        response = self.client.get(url)
        self.assertIn("dataset", str(response.context))

    def test_show_metrics_shows_metrics_charts(self):
        self.client.login(username=self.username, password=self.password)

        area = Area.objects.create(text="Area")
        activity = Activity.objects.create(text="Activity", area=area)
        metric = Metric.objects.create(text="Metric 1", activity=activity, wikipedia_created=4)

        url = reverse("metrics:metrics")
        response = self.client.get(url)

        self.assertIn("wikipedia_created", str(response.context["total_sum"]))
        self.assertIn("<canvas id=\"wikipedia_pie_chart\">", str(response.content))
        self.assertIn("<canvas id=\"wikipedia_timeline_chart\">", str(response.content))
        self.assertNotIn("<canvas id=\"commons_pie_chart\">", str(response.content))

    def test_show_metrics_shows_projects_metrics_as_charts(self):
        self.client.login(username=self.username, password=self.password)

        area = Area.objects.create(text="Area")
        activity = Activity.objects.create(text="Activity", area=area)
        project = Project.objects.create(text="Project")
        metric = Metric.objects.create(text="Metric 1", activity=activity, wikipedia_created=4)
        metric.project.add(project)
        metric.save()

        url = reverse("metrics:metrics")
        response = self.client.get(url)

        self.assertIn(project.text, str(response.context["projects_metrics"]))


class MetricFunctionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.team_area = TeamArea.objects.create(text="Area")
        self.area = Area.objects.create(text="Area")
        self.activity_1 = Activity.objects.create(text="Activity 1")
        self.activity_2 = Activity.objects.create(text="Activity 2")
        self.metric_1 = Metric.objects.create(text="Metric 1", activity=self.activity_1)
        self.metric_2 = Metric.objects.create(text="Metric 2", activity=self.activity_1)
        self.metric_3 = Metric.objects.create(text="Metric 3", activity=self.activity_2)

        self.report_1 = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=self.activity_1,
            area_responsible=self.team_area,
            initial_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            description="Report 1",
            links="https://testlink.com",
            learning="Learning" * 60,
        )

        self.report_2 = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=self.activity_1,
            area_responsible=self.team_area,
            initial_date=datetime.now().date() + timedelta(days=1),
            end_date=datetime.now().date() + timedelta(days=2),
            description="Report 2",
            links="https://testlink.com",
            learning="Learning" * 60,
        )

        self.report_3 = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=self.activity_1,
            area_responsible=self.team_area,
            initial_date=datetime.now().date() + timedelta(days=1),
            end_date=datetime.now().date() + timedelta(days=2),
            description="Report 3",
            links="https://testlink.com",
            learning="Learning" * 60,
        )

        self.editor_1 = Editor.objects.create(username="Editor 1")
        self.editor_2 = Editor.objects.create(username="Editor 2")
        self.editor_3 = Editor.objects.create(username="Editor 3")

    def test_get_aggregated_metrics_data_with_data(self):
        self.metric_1.wikipedia_created = 1
        self.metric_2.number_of_editors = 4
        self.metric_3.number_of_editors = 2
        self.metric_1.save()
        self.metric_2.save()
        self.metric_3.save()

        aggregated_metrics = get_aggregated_metrics_data()
        self.assertEqual(aggregated_metrics["editors"], self.metric_2.number_of_editors + self.metric_3.number_of_editors)
        self.assertEqual(aggregated_metrics["wikipedia_created"], self.metric_1.wikipedia_created)
        self.assertEqual(aggregated_metrics["wikipedia_edited"], 0)

    def test_get_aggregated_metrics_data_without_data(self):
        aggregated_metrics = get_aggregated_metrics_data()
        self.assertEqual(aggregated_metrics["editors"], 0)
        self.assertEqual(aggregated_metrics["wikipedia_created"], 0)
        self.assertEqual(aggregated_metrics["wikipedia_edited"], 0)

    def test_get_aggregated_metrics_data_done_with_data(self):
        self.report_1.wikipedia_created = 1
        self.report_1.editors.add(self.editor_1)
        self.report_1.editors.add(self.editor_2)
        self.report_2.editors.add(self.editor_3)
        self.report_3.editors.add(self.editor_3)
        self.report_1.save()
        self.report_2.save()
        self.report_3.save()

        aggregated_metrics_done = get_aggregated_metrics_data_done()
        self.assertEqual(aggregated_metrics_done["editors"], self.report_1.editors.count() + self.report_2.editors.count() + self.report_3.editors.count())
        self.assertEqual(aggregated_metrics_done["wikipedia_created"], self.report_1.wikipedia_created)
        self.assertEqual(aggregated_metrics_done["wikipedia_edited"], 0)

    def test_get_aggregated_metrics_data_done_without_data(self):
        aggregated_metrics_done = get_aggregated_metrics_data_done()
        self.assertEqual(aggregated_metrics_done["editors"], 0)
        self.assertEqual(aggregated_metrics_done["wikipedia_created"], 0)
        self.assertEqual(aggregated_metrics_done["wikipedia_edited"], 0)

    def test_get_metrics_and_aggregate_per_project_with_data_and_metric_unclear(self):
        project = Project.objects.create(text="Project")
        self.metric_2.project.add(project)
        self.metric_2.save()
        area = Area.objects.create(text="Area")
        area.project.add(project)
        area.save()
        self.activity_1.area = area
        self.activity_1.save()
        aggregated_metrics = get_metrics_and_aggregate_per_project()
        self.assertEqual(list(aggregated_metrics.keys())[0], project.id)
        self.assertEqual(aggregated_metrics[1]["project"], project.text)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_id"], self.activity_1.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity"], self.activity_1.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"].keys())[0], self.metric_2.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["title"], self.metric_2.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"].keys())[0], "Other metric")
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"]["Other metric"]["goal"], "-")
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"]["Other metric"]["done"], "-")

    def test_get_metrics_and_aggregate_per_project_with_goal_but_none_done(self):
        project = Project.objects.create(text="Project")
        self.metric_2.project.add(project)
        self.metric_2.wikipedia_created = 500
        self.metric_2.save()
        area = Area.objects.create(text="Area")
        area.project.add(project)
        area.save()
        self.activity_1.area = area
        self.activity_1.save()
        aggregated_metrics = get_metrics_and_aggregate_per_project()
        self.assertEqual(list(aggregated_metrics.keys())[0], project.id)
        self.assertEqual(aggregated_metrics[1]["project"], project.text)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_id"], self.activity_1.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity"], self.activity_1.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"].keys())[0], self.metric_2.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["title"], self.metric_2.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"].keys())[0], "Wikipedia")
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"]["Wikipedia"]["goal"], 500)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"]["Wikipedia"]["done"], 0)

    def test_get_metrics_and_aggregate_per_project_with_goal_and_some_done(self):
        project = Project.objects.create(text="Project")
        self.metric_2.project.add(project)
        self.metric_2.wikipedia_created = 500
        self.metric_2.save()
        area = Area.objects.create(text="Area")
        area.project.add(project)
        area.save()
        self.activity_1.area = area
        self.activity_1.save()

        self.report_3.metrics_related.add(self.metric_2.id)
        self.report_3.wikipedia_edited = 200
        self.report_3.save()
        aggregated_metrics = get_metrics_and_aggregate_per_project()
        self.assertEqual(list(aggregated_metrics.keys())[0], project.id)
        self.assertEqual(aggregated_metrics[1]["project"], project.text)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_id"], self.activity_1.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity"], self.activity_1.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"].keys())[0], self.metric_2.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["title"], self.metric_2.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"].keys())[0], "Wikipedia")
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"]["Wikipedia"]["goal"], 500)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][2]["metrics"]["Wikipedia"]["done"], 200)

    def test_get_metrics_and_aggregate_per_project_without_data(self):
        aggregated_metrics = get_metrics_and_aggregate_per_project()
        self.assertEqual(aggregated_metrics, {})

    def test_get_activities_with_data(self):
        self.report_1.wikipedia_created = 1
        self.report_2.editors.add(self.editor_1)
        self.report_1.save()
        self.report_2.save()

        chart_data = get_activities()
        self.assertEqual(chart_data, {"wikipedia": [{"x": str(datetime.now().date() + timedelta(days=1)),
                                                     "y": self.report_1.wikipedia_created,
                                                     "label": self.report_1.description}],
                                      "commons": [],
                                      "wikidata": [],
                                      "wikiversity": [],
                                      "wikibooks": [],
                                      "wikisource": [],
                                      "wikinews": [],
                                      "wikiquote": [],
                                      "wiktionary": [],
                                      "wikivoyage": [],
                                      "wikispecies": [],
                                      "metawiki": [],
                                      "mediawiki": [],
                                      "participants": [],
                                      "resources": [],
                                      "feedbacks": [],
                                      "editors": [{"x": str(datetime.now().date() + timedelta(days=2)),
                                                   "y": self.report_2.editors.count(),
                                                   "label": self.report_2.description}],
                                      "organizers": [],
                                      "partnerships": []})

    def test_get_activities_without_data(self):
        chart_data = get_activities()
        self.assertEqual(chart_data, {"wikipedia": [], "commons": [], "wikidata": [], "wikiversity": [], "wikibooks": [], "wikisource": [], "wikinews": [], "wikiquote": [], "wiktionary": [], "wikivoyage": [], "wikispecies": [], "metawiki": [], "mediawiki": [], "participants": [], "resources": [], "feedbacks": [], "editors": [], "organizers": [], "partnerships": []})

    def test_get_chart_data_with_data(self):
        self.report_1.wikipedia_created = 1
        self.report_2.wikipedia_edited = 2
        self.report_3.wikipedia_created = 3
        self.report_3.wikipedia_edited = 4
        self.report_1.save()
        self.report_2.save()
        self.report_3.save()

        activities = Report.objects.all().order_by("end_date")
        chart_data = get_chart_data(activities, "wikipedia_created", "wikipedia_edited")
        self.assertEqual(chart_data, [{"x": str(datetime.now().date() + timedelta(days=1)),
                                       "y": self.report_1.wikipedia_created + self.report_1.wikipedia_edited,
                                       "label": self.report_1.description},
                                      {"x": str(datetime.now().date() + timedelta(days=2)),
                                       "y": self.report_1.wikipedia_created + self.report_1.wikipedia_edited + self.report_2.wikipedia_created + self.report_2.wikipedia_edited,
                                       "label": self.report_2.description},
                                      {"x": str(datetime.now().date() + timedelta(days=2)),
                                       "y": self.report_1.wikipedia_created + self.report_1.wikipedia_edited + self.report_2.wikipedia_created + self.report_2.wikipedia_edited + self.report_3.wikipedia_created + self.report_3.wikipedia_edited,
                                       "label": self.report_3.description}])

    def test_get_chart_data_without_data(self):
        activities = Report.objects.all().order_by("end_date")
        chart_data = get_chart_data(activities, "wikipedia_created", "wikipedia_edited")
        self.assertEqual(chart_data, [])

    def test_get_chart_data_many_to_many_with_data(self):
        self.report_1.editors.add(self.editor_1)
        self.report_1.editors.add(self.editor_2)
        self.report_2.editors.add(self.editor_3)
        self.report_1.save()
        self.report_2.save()

        activities = Report.objects.all().order_by("end_date")
        chart_data = get_chart_data_many_to_many(activities, "editors")
        self.assertEqual(chart_data, [{"x": str(datetime.now().date() + timedelta(days=1)),
                                       "y": self.report_1.editors.count(),
                                       "label": self.report_1.description},
                                      {"x": str(datetime.now().date() + timedelta(days=2)),
                                       "y": self.report_1.editors.count() + self.report_2.editors.count(),
                                       "label": self.report_2.description}])

    def test_get_chart_data_many_to_many_without_data(self):
        activities = Report.objects.all().order_by("end_date")
        chart_data = get_chart_data_many_to_many(activities, "editors")
        self.assertEqual(chart_data, [])


class TagsTests(TestCase):
    def test_categorize_for_0(self):
        result = categorize(0, 100)
        self.assertEqual(result, 1)

    def test_categorize_for_1(self):
        result = categorize(1, 100)
        self.assertEqual(result, 1)

    def test_categorize_for_26(self):
        result = categorize(26, 100)
        self.assertEqual(result, 2)

    def test_categorize_for_51(self):
        result = categorize(51, 100)
        self.assertEqual(result, 3)

    def test_categorize_for_76(self):
        result = categorize(76, 100)
        self.assertEqual(result, 4)

    def test_categorize_for_99(self):
        result = categorize(99, 100)
        self.assertEqual(result, 4)

    def test_categorize_for_100(self):
        result = categorize(100, 100)
        self.assertEqual(result, 5)

    def test_categorize_for_more_than_100(self):
        result = categorize(150, 100)
        self.assertEqual(result, 5)

    def test_categorize_for_text(self):
        result = categorize("invalid", 100)
        self.assertEqual(result, "-")

    def test_perc_for_0(self):
        result = perc(0, 100)
        self.assertEqual(result, "0%")

    def test_perc_for_1(self):
        result = perc(1, 100)
        self.assertEqual(result, "1%")

    def test_perc_for_26(self):
        result = perc(26, 100)
        self.assertEqual(result, "26%")

    def test_perc_for_51(self):
        result = perc(51, 100)
        self.assertEqual(result, "51%")

    def test_perc_for_76(self):
        result = perc(76, 100)
        self.assertEqual(result, "76%")

    def test_perc_for_99(self):
        result = perc(99, 100)
        self.assertEqual(result, "99%")

    def test_perc_for_100(self):
        result = perc(100, 100)
        self.assertEqual(result, "100%")

    def test_perc_for_more_than_100(self):
        result = perc(150, 100)
        self.assertEqual(result, "100%")

    def test_perc_for_text(self):
        result = perc("invalid", 100)
        self.assertEqual(result, "-")