from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("name", "initial_date", "end_date", "area_responsible", "area_involved")
        widgets = {
            "name": forms.TextInput(attrs={'required': True}),
            "initial_date": forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'required': True}),
            "end_date": forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'required': True}),
            "area_responsible": forms.Select(attrs={'required': True}),
            "area_involved": forms.SelectMultiple(attrs={'size': 5})
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        initials = {}

        if self.instance.pk:
            initials.update({
                'area_involved': self.instance.area_involved.all()
            })

        for field, initial in initials.items():
            self.fields[field].initial = initial
