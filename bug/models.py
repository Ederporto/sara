from django.db import models
from users.models import UserProfile
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Bug(models.Model):
    class Status(models.TextChoices):
        TODO = "1", _("To do")
        PROG = "2", _("In progress")
        TEST = "3", _("Testing")
        DONE = "4", _("Done")

    class BugType(models.TextChoices):
        ERROR = "1", _("Error")
        IMPROVEMENT = "2", _("Improvement request")
        NEWFEATURE = "3", _("New feature request")
        CLARIFICATION = "4", _("Question or clarification")

    title = models.CharField(_("Title"), max_length=140)
    description = models.TextField(_("Description"), max_length=500)
    type_of_bug = models.CharField(_("Type"), max_length=1, choices=BugType.choices, default=BugType.ERROR)
    status = models.CharField(_("Status"), max_length=1, choices=Status.choices, default=Status.TODO)
    date_of_report = models.DateField(_("Date of report"), auto_now_add=True, editable=False)
    reporter = models.ForeignKey(UserProfile, on_delete=models.RESTRICT, related_name="reporter", editable=False)
    update_date = models.DateField(_("Update date"), auto_now=True)

    def __str__(self):
        return self.title


class Observation(models.Model):
    bug_report = models.OneToOneField(Bug, on_delete=models.CASCADE, related_name="observation")
    observation = models.TextField(_("Observation"), max_length=500)
    date_of_answer = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.observation
