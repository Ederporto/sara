from django.utils import timezone
from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.db.models.functions import Lower
from .models import Report, StrategicLearningQuestion, LearningArea, AreaActivated, Funding, Partner, Technology,\
    Editor, Organizer
from metrics.models import Area
from strategy.models import StrategicAxis
from users.models import TeamArea, UserProfile


class NewReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = "__all__"
        exclude = ["created_by", "created_at", "modified_by", "modified_at"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(NewReportForm, self).__init__(*args, **kwargs)
        self.fields["activity_associated"].choices = activities_associated_as_choices()
        self.fields["directions_related"].choices = directions_associated_as_choices()
        self.fields["learning_questions_related"].choices = learning_questions_as_choices()
        self.fields["area_responsible"].queryset = TeamArea.objects.order_by(Lower("text"))
        self.fields["funding_associated"].queryset = Funding.objects.order_by(Lower("name"))
        self.fields["area_activated"].queryset = AreaActivated.objects.order_by(Lower("text"))
        self.fields["partners_activated"].queryset = Partner.objects.order_by(Lower("name"))
        if self.instance:
            self.fields["area_responsible"].initial = self.instance.area_responsible_id
        else:
            self.fields["area_responsible"].initial = area_responsible_of_user(user)
        self.fields["technologies_used"].queryset = Technology.objects.order_by(Lower("name"))


    def clean_editors(self):
        editors_string = self.data.get("editors_string", "")
        editors_list = editors_string.split("\r\n") if editors_string else []
        editors = []
        for editor in editors_list:
            editor_object, created = Editor.objects.get_or_create(username=editor)
            editors.append(editor_object)
        return editors

    def clean_organizers(self):
        organizers_string = self.data.get("organizers_string", "")
        organizers_list = organizers_string.split("\r\n") if organizers_string else []
        organizers = []
        for organizer in organizers_list:
            organizer_name, institution_name = (organizer + ";").split(";", maxsplit=1)
            organizer_object, created = Organizer.objects.get_or_create(name=organizer_name)
            if institution_name:
                for partner_name in institution_name.split(";"):
                    if partner_name:
                        partner, partner_created = Partner.objects.get_or_create(name=partner_name)
                        organizer_object.institution.add(partner)
                organizer_object.save()
            organizers.append(organizer_object)
        return organizers

    def clean_initial_date(self):
        initial_date = self.cleaned_data.get('initial_date')
        return initial_date

    def clean_end_date(self):
        initial_date = self.cleaned_data.get('initial_date')
        end_date = self.cleaned_data.get('end_date')

        if end_date:
            return end_date
        else:
            return initial_date

    def save(self, commit=True, user=None, *args, **kwargs):
        report = super(NewReportForm, self).save(commit=False)
        if commit:
            user_profile = get_object_or_404(UserProfile, user=user)
            report.created_by = user_profile
            report.modified_by = user_profile
            report.save()
            report.editors.clear()
            report.organizers.clear()
            report.editors.set(self.cleaned_data['editors'])
            report.organizers.set(self.cleaned_data['organizers'])
            report.partners_activated.set(self.cleaned_data['partners_activated'])
            report.technologies_used.set(self.cleaned_data['technologies_used'])
            report.area_activated.set(self.cleaned_data['area_activated'])
            report.directions_related.set(self.cleaned_data['directions_related'])
            report.learning_questions_related.set(self.cleaned_data['learning_questions_related'])
            report.end_date = report.initial_date
        return report


def area_responsible_of_user(user):
    try:
        team_area = TeamArea.objects.get(team_area_of_position=user.userprofile.position)
        return team_area.id
    except TeamArea.DoesNotExist:
        return ""


def activities_associated_as_choices():
    areas = []
    for area in Area.objects.all():
        activities = []
        for activity in area.activities.all():
            activities.append((activity.id, activity.text + " (" + activity.code + ")"))
        areas.append((area.text, tuple(activities)))
    return tuple(areas)


def directions_associated_as_choices():
    axes = []
    for axis in StrategicAxis.objects.all():
        directions = []
        for direction in axis.directions.all():
            directions.append((direction.id, direction.text))
        axes.append((axis.text, tuple(directions)))

    return tuple(axes)


def learning_questions_as_choices():
    learning_areas = []
    for learning_area in LearningArea.objects.all():
        learning_questions = []
        for learning_question in learning_area.strategic_question.all():
            learning_questions.append((learning_question.id, learning_question.text))
        learning_areas.append((learning_area.text, tuple(learning_questions)))

    return tuple(learning_areas)


def learning_areas_as_choices():
    areas = []
    for area in LearningArea.objects.all():
        new_category = []
        questions = []
        for question in area.strategic_question.all():
            questions.append([question.id, question.text])
            new_category = [area.text, questions]
        areas.append(new_category)

    return areas


class AreaActivatedForm(forms.ModelForm):
    class Meta:
        model = AreaActivated
        fields = "__all__"
        widgets = {
            "text": forms.Textarea(attrs={'type': 'textarea', 'rows': 5, 'required': True}),
            "contact": forms.Textarea(attrs={'type': 'textarea', 'rows': 5})
        }


class FundingForm(forms.ModelForm):
    class Meta:
        model = Funding
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={'required': True}),
            "project": forms.TextInput(attrs={'required': True}),
            "value": forms.NumberInput()
        }

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if not value:
            return 0


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={'required': True}),
            "website": forms.TextInput()
        }


class TechnologyForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={'required': True}),
            "value": forms.NumberInput()
        }