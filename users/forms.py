from django import forms
from django.contrib.auth.models import User, Group
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("professional_wiki_handle", "personal_wiki_handle", "wikidata_item", "photograph", "gender",
                  "linkedin", "lattes", "orcid", "google_scholar", "twitter", "facebook", "instagram")
        widgets = {
            "professional_wiki_handle": forms.TextInput(attrs={'required': True})
        }


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
