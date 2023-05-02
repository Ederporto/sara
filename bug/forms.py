from django import forms
from .models import Bug, Observation


class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = "__all__"
        exclude = ["status"]

    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)


class BugUpdateForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(BugUpdateForm, self).__init__(*args, **kwargs)


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = "__all__"
        exclude = ["bug_report"]

    def __init__(self, *args, **kwargs):
        super(ObservationForm, self).__init__(*args, **kwargs)
