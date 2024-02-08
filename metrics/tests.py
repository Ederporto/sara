from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from .models import Objective, Area, Metric, Activity, Project
from report.models import Report, Editor
from users.models import User, UserProfile, TeamArea
from strategy.models import StrategicAxis
from .views import get_metrics_and_aggregate_per_project
from django.urls import reverse
from django.contrib.auth.models import Permission
from datetime import datetime, timedelta
from metrics.templatetags.metricstags import categorize, perc, bool_yesno, is_yesno
from django.utils.translation import gettext_lazy as _


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
        self.project = Project.objects.create(text=self.text, active=self.status)

    def test_project_str_returns_text(self):
        self.assertEqual(str(self.project), self.text)

    def test_project_text_cant_be_empty(self):
        with self.assertRaises(ValidationError):
            empty_project = Project(text="")
            empty_project.full_clean()


class MetricModelTests(TestCase):
    def setUp(self):
        self.area = Area.objects.create(text="Area")
        self.activity = Activity.objects.create(text="Activity", area=self.area)
        self.metric = Metric.objects.create(text="Metric", activity=self.activity)

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
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.view_metrics_permission = Permission.objects.get(codename="view_metric")
        self.change_metrics_permission = Permission.objects.get(codename="change_metric")
        self.user.user_permissions.add(self.view_metrics_permission)
        self.user.user_permissions.add(self.change_metrics_permission)

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
        url = reverse("metrics:show_activities")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://meta.wikimedia.org/wiki/Wiki_Movement_Brazil_User_Group/Plan_of_Activities")

    def test_show_metrics_per_project(self):
        self.client.login(username=self.username, password=self.password)
        Project.objects.create(text="Project", current_poa=True)
        url = reverse("metrics:per_project")

        response = self.client.get(url)
        self.assertIn("dataset", str(response.context))

    def test_show_plan_of_activities_and_its_operational_metrics_if_they_exist(self):
        self.client.login(username=self.username, password=self.password)
        project = Project.objects.create(text="Plan of activities", current_poa=True)
        area = Area.objects.create(text="Area")
        area.project.add(project)
        area.save()
        activity = Activity.objects.create(text="Activity", area=area)
        metric_1 = Metric.objects.create(text="Metric 1", boolean_type=True, activity=activity)
        metric_1.project.add(project)
        metric_1.save()
        metric_2 = Metric.objects.create(text="Metric 2", is_operation=True, activity=activity)
        metric_2.project.add(project)
        metric_2.save()

        url = reverse("metrics:per_project")
        response = self.client.get(url)
        self.assertIn("poa_dataset", str(response.context))
        self.assertEqual(response.context["poa_dataset"][1]["project_metrics"][0]["activity_metrics"][1]["title"], str(metric_1))
        self.assertEqual(response.context["poa_dataset"][1]["project_metrics"][1]["activity_metrics"][2]["title"], str(metric_2))

    def test_update_metrics(self):
        self.client.login(username=self.username, password=self.password)
        Project.objects.create(text="Plan of Activities", current_poa=True)

        area = Area.objects.create(text="Area")
        activity = Activity.objects.create(text="Activity", area=area)
        project_1 = Project.objects.create(text="Wikimedia Community Fund", main_funding=True)

        metric = Metric.objects.create(text="Metric 1", activity=activity, number_of_editors=10)
        metric.project.add(project_1)

        team_area = TeamArea.objects.create(text="Area")
        activity_1 = Activity.objects.create(text="Activity 1")
        metric_2 = Metric.objects.create(text="Metric 2", activity=activity_1, number_of_editors=9)

        report_1 = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=activity_1,
            area_responsible=team_area,
            initial_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            description="Report 1",
            links="https://testlink.com",
            learning="Learning" * 60,
        )
        report_1.metrics_related.add(metric_2)
        report_1.save()

        url = reverse("metrics:update_metrics")
        response = self.client.get(url, follow=True)

        self.assertRedirects(response, reverse('metrics:per_project'))

    def test_do_not_show_reports_associated_to_a_metric_to_users_without_permission(self):
        self.user.user_permissions.remove(self.view_metrics_permission)
        self.client.login(username=self.username, password=self.password)

        area = Area.objects.create(text="Area")
        activity = Activity.objects.create(text="Activity", area=area)
        metric = Metric.objects.create(text="Metric 1", activity=activity, number_of_editors=10)

        url = reverse("metrics:metrics_reports", args=[metric.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_show_reports_associated_to_a_metric_only_to_users_with_permission(self):
        self.client.login(username=self.username, password=self.password)

        area = Area.objects.create(text="Area")
        activity = Activity.objects.create(text="Activity", area=area)
        metric = Metric.objects.create(text="Metric 1", activity=activity, number_of_editors=10)
        team_area = TeamArea.objects.create(text="Area")
        report_1 = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=activity,
            area_responsible=team_area,
            initial_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            description="Report 1",
            links="https://testlink.com",
            learning="Learning" * 60,
        )
        report_1.metrics_related.add(metric)
        report_1.save()

        url = reverse("metrics:metrics_reports", args=[metric.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "metrics/list_metrics_reports.html")

    def test_redirects_to_list_of_metrics_per_project_if_metric_id_does_not_exist(self):
        self.client.login(username=self.username, password=self.password)

        project = Project.objects.create(text="Plan of Activities", current_poa=True)
        area = Area.objects.create(text="Area")
        area.project.add(project)
        area.save()
        activity = Activity.objects.create(text="Activity", area=area)
        metric = Metric.objects.create(text="Metric 1", activity=activity, number_of_editors=10)
        metric.project.add(project)
        metric.save()
        team_area = TeamArea.objects.create(text="Area")
        report_1 = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=activity,
            area_responsible=team_area,
            initial_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            description="Report 1",
            links="https://testlink.com",
            learning="Learning" * 60,
        )
        report_1.metrics_related.add(metric)
        report_1.save()

        url = reverse("metrics:metrics_reports", args=[123456789])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('metrics:per_project')}")


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

    def test_get_metrics_and_aggregate_per_project_with_data_and_metric_unclear_when_id_ge_1(self):
        project = Project.objects.create(text="Project")
        self.metric_3.project.add(project)
        self.metric_3.save()
        area = Area.objects.create(text="Area")
        area.project.add(project)
        area.save()
        self.activity_2.area = area
        self.activity_2.save()

        self.report_2.activity_associated = self.activity_2
        self.report_2.save()
        aggregated_metrics = get_metrics_and_aggregate_per_project()
        self.assertEqual(list(aggregated_metrics.keys())[0], project.id)
        self.assertEqual(aggregated_metrics[1]["project"], project.text)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_id"], self.activity_2.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity"], self.activity_2.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"].keys())[0], self.metric_3.id)
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][3]["title"], self.metric_3.text)
        self.assertEqual(list(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][3]["metrics"].keys())[0], "Other metric")
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][3]["metrics"]["Other metric"]["goal"], "-")
        self.assertEqual(aggregated_metrics[1]["project_metrics"][0]["activity_metrics"][3]["metrics"]["Other metric"]["done"], "-")

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
        self.assertEqual(result, "150%")

    def test_perc_for_text(self):
        result = perc("invalid", 100)
        self.assertEqual(result, "-")

    def test_bool_yesno_returns_yes_if_true(self):
        result = bool_yesno(True)
        self.assertEqual(result, _("Yes"))

    def test_bool_yesno_returns_no_if_false(self):
        result = bool_yesno(False)
        self.assertEqual(result, _("No"))

    def test_bool_yesno_returns_value_if_not_boolean(self):
        result = bool_yesno("Test")
        self.assertEqual(result, _("Test"))

    def test_bool_is_yesno_returns_true_if_boolean(self):
        result = is_yesno(True)
        self.assertTrue(result)

    def test_bool_is_yesno_returns_false_if_not_boolean(self):
        result = is_yesno(2)
        self.assertFalse(result)

    def test_bool_is_yesno_returns_false_even_if_is_0_or_1(self):
        result = is_yesno(0)
        self.assertFalse(result)

        result = is_yesno(1)
        self.assertFalse(result)