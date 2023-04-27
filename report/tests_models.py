from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Funding, Editor, Organizer, Partner, Technology, AreaActivated, LearningArea,\
    StrategicLearningQuestion, EvaluationObjective, Report, StrategicAxis
from users.models import TeamArea, UserProfile, User
from metrics.models import Activity
from strategy.models import Direction
from datetime import datetime, timedelta


class FundingModelTest(TestCase):
    def setUp(self):
        self.name = "Funding"
        self.value = 1000
        self.funding = Funding.objects.create(name=self.name, value=self.value)

    def test_funding_str_method_returns_its_text(self):
        self.assertEqual(str(self.funding), self.name)

    def test_funding_value(self):
        funding_value = self.funding.value
        self.assertEqual(funding_value, self.value)


class EditorModelTest(TestCase):
    def setUp(self):
        self.username = "Editor"
        self.editor = Editor.objects.create(username=self.username)

    def test_editor_str_method_returns_its_username(self):
        self.assertEqual(str(self.editor), self.username)


class PartnerModelTest(TestCase):
    def setUp(self):
        self.name = "Partner"
        self.partner = Partner.objects.create(name=self.name)

    def test_partner_str_method_returns_its_name(self):
        self.assertEqual(str(self.partner), self.name)


class OrganizerModelTest(TestCase):
    def setUp(self):
        self.organizer_name = "Organizer"
        self.partner = Partner.objects.create(name="Partner")
        self.organizer = Organizer.objects.create(name=self.organizer_name)
        self.organizer.institution.add(self.partner)

    def test_organizer_str_method_returns_their_name(self):
        self.assertEqual(str(self.organizer), self.organizer_name)

    def test_organizer_institution(self):
        institutions = self.organizer.institution.all()
        self.assertEqual(institutions.count(), 1)
        self.assertEqual(institutions.first(), self.partner)


class TechnologyModelTest(TestCase):
    def setUp(self):
        self.name = "Technology"
        self.technology = Technology.objects.create(name=self.name)

    def test_partner_str_method_returns_its_name(self):
        self.assertEqual(str(self.technology), self.name)


class AreaActivatedModelTest(TestCase):
    def setUp(self):
        self.text = "Area Activated"
        self.area_activated = AreaActivated.objects.create(text=self.text)

    def test_area_activated_str_method_returns_the_text(self):
        self.assertEqual(str(self.area_activated), self.text)

    def test_area_activated_contact(self):
        self.area_activated.contact = "Contact"
        self.area_activated.save()
        area_activated_contact = self.area_activated.contact
        self.assertEqual(area_activated_contact, "Contact")

    def test_area_activated_clean_method(self):
        area_activated = AreaActivated()
        with self.assertRaises(ValidationError):
            area_activated.clean()

    def test_creating_team_area_creates_an_area_activated_instance(self):
        self.assertEqual(AreaActivated.objects.count(), 1)
        self.assertFalse(AreaActivated.objects.filter(text="Team Area").exists())
        TeamArea.objects.create(text="Team Area", code="Code")
        self.assertEqual(AreaActivated.objects.count(), 2)
        self.assertTrue(AreaActivated.objects.filter(text="Team Area").exists())


class LearningAreaModelTest(TestCase):
    def setUp(self):
        self.learning_area_text = "Test Learning Area"
        self.learning_area = LearningArea.objects.create(text=self.learning_area_text)

    def test_learning_area_str_method_returns_its_text(self):
        self.assertEqual(str(self.learning_area), self.learning_area_text)

    def test_learning_area_clean_method(self):
        learning_area = LearningArea()
        with self.assertRaises(ValidationError):
            learning_area.clean()


class StrategicLearningQuestionModelTest(TestCase):
    def setUp(self):
        self.learning_area = LearningArea.objects.create(text="Learning Area")
        self.strategic_question_text = "Strategic Learning Question"
        self.strategic_question = StrategicLearningQuestion.objects.create(text=self.strategic_question_text,
                                                                           learning_area=self.learning_area)

    def test_strategic_learning_question_str_method_returns_its_text(self):
        self.assertEqual(str(self.strategic_question), self.strategic_question_text)

    def test_strategic_learning_question_learning_area(self):
        self.assertEqual(self.strategic_question.learning_area, self.learning_area)

    def test_strategic_learning_question_clean_method(self):
        strategic_learning_question = StrategicLearningQuestion()
        with self.assertRaises(ValidationError):
            strategic_learning_question.clean()


class EvaluationObjectiveModelTest(TestCase):
    def setUp(self):
        self.learning_area = LearningArea.objects.create(text="Test Learning Area")
        self.evaluation_objective_text = "Test Evaluation Objective"
        self.evaluation_objective = EvaluationObjective.objects.create(text=self.evaluation_objective_text,
                                                                       learning_area_of_objective=self.learning_area)

    def test_evaluation_objective_str_method_returns_its_text(self):
        self.assertEqual(str(self.evaluation_objective), self.evaluation_objective_text)

    def test_evaluation_objective_learning_area(self):
        self.assertEqual(self.evaluation_objective.learning_area_of_objective, self.learning_area)

    def test_evaluation_objective_clean_method(self):
        evaluation_objective = EvaluationObjective()
        with self.assertRaises(ValidationError):
            evaluation_objective.clean()


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.team_area = TeamArea.objects.create(text="Area")
        self.activity = Activity.objects.create(text="Activity")
        self.funding = Funding.objects.create(name="Funding")
        strategic_axis = StrategicAxis.objects.create(text="Strategic Axis")
        self.direction = Direction.objects.create(text="Direction", strategic_axis=strategic_axis)
        learning_area = LearningArea.objects.create(text="Learning area")
        self.slq = StrategicLearningQuestion.objects.create(text="SLQ", learning_area=learning_area)

    def test_report_creation(self):
        report = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=self.activity,
            area_responsible=self.team_area,
            initial_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            description="Report",
            links="https://testlink.com",
            participants=10,
            resources=5,
            feedbacks=3,
            learning="Learning"*60,
        )
        self.assertEqual(report.description, "Report")

    def test_report_end_date_default(self):
        report = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=self.activity,
            area_responsible=self.team_area,
            initial_date=datetime.now().date(),
            description="Report",
            links="https://testlink.com",
            participants=10,
            resources=5,
            feedbacks=3,
            learning="Learning",
        )
        self.assertEqual(report.end_date, report.initial_date)

    def test_report_string_representation(self):
        report = Report.objects.create(
            created_by=self.user_profile,
            modified_by=self.user_profile,
            activity_associated=self.activity,
            area_responsible=self.team_area,
            initial_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            description="Report",
            links="https://testlink.com",
            participants=10,
            resources=5,
            feedbacks=3,
            learning="Learning",
        )
        self.assertEqual(str(report), "Report")


