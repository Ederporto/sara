from django import forms
from .models import Report, StrategicLearningQuestion, LearningArea, AreaActivated, Funding, Partner, Technology
from metrics.models import Area
from strategy.models import StrategicAxis


class NewReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = "__all__"
        exclude = ["created_by", "created_at", "modified_by", "modified_at"]

    def __init__(self, *args, **kwargs):
        super(NewReportForm, self).__init__(*args, **kwargs)
        self.fields['activity_associated'].choices = activities_associated_as_choices()
        self.fields['directions_related'].choices = directions_associated_as_choices()
        self.fields['learning_questions_related'].choices = learning_questions_as_choices()


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


class StrategicLearningQuestionsForm(forms.ModelForm):
    class Meta:
        model = StrategicLearningQuestion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(StrategicLearningQuestionsForm, self).__init__(*args, **kwargs)
        self.fields['learning_area'].choices = learning_areas_as_choices()


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
            "value": forms.NumberInput()
        }


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