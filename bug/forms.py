from django import forms
from .models import Bug


class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ("title", "type_of_bug", "description")
        widgets = {
            "type_of_bug": forms.Select(attrs={'required': True}),
            "description": forms.Textarea(attrs={'required': True, 'rows': 4})
        }


class BugReportForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ("title", "type_of_bug", "description", "update_date", "status", "observation")
        widgets = {
            "type_of_bug": forms.Select(attrs={'required': True}),
            "description": forms.Textarea(attrs={'required': True, 'rows': 4}),
            "observation": forms.Textarea(attrs={'required': False, 'rows': 4})
        }
