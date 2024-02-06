from django import forms
from agenda.models import Event


class EventForm(forms.ModelForm):
    """
    Form for creating and updating Event instances.

    This form provides fields for creating and updating Event instances.
    It uses the Event model and specifies the fields to include in the
    form along with their corresponding widgets for rendering in HTML.

    Meta:
        - model: The model associated with the form.
        - fields: The fields from the model to include in the form.
        - widgets: The widgets to use for rendering form fields in HTML.

    Methods:
        - __init__: Initializes the form instance, populating initial values for fields.
    """

    class Meta:
        model = Event
        fields = ("name", "initial_date", "end_date", "area_responsible", "area_involved", "metric_associated")
        widgets = {
            "name": forms.TextInput(attrs={"required": True}),
            "initial_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "required": True}),
            "end_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "required": True}),
            "area_responsible": forms.Select(attrs={"required": True, "class":"select-with-text"}),
            "area_involved": forms.SelectMultiple(attrs={"class":"select-with-text"}),
            "metric_associated": forms.SelectMultiple(attrs={"class":"select-with-text"})
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        initials = {}

        if self.instance.pk:
            initials.update({"area_involved": self.instance.area_involved.all()})
            initials.update({"area_involved": self.instance.metric_associated.all()})

        for field, initial in initials.items():
            self.fields[field].initial = initial
