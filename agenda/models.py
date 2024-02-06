from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from users.models import TeamArea
from metrics.models import Metric


# CALENDAR OF EVENTS
class Event(models.Model):
    """
    Represents an event in the agenda of the team.

    Attributes:
        - name: Title of the event
        - initial_date: Date of the begining of the event
        - end_date: Date of the ending of the event
        - area_responsible: Area responsible for the event
        - area_involved: Areas involved in/activated for the event

    Meta:
        - verbose_name: A human-readable name for the model (singular).
        - verbose_name_plural: A human-readable name for the model (plural).

    Methods:
        - __str__: Returns a string representation of the event, including the name and date range.
        - clean: Validates that the event has a name, initial date, and end date.
    """
    name = models.CharField(max_length=420)
    initial_date = models.DateField()
    end_date = models.DateField()
    area_responsible = models.ForeignKey(TeamArea, on_delete=models.RESTRICT, related_name="area_responsible")
    area_involved = models.ManyToManyField(TeamArea, related_name="area_involved", blank=True)
    metric_associated = models.ManyToManyField(Metric, related_name="event_metrics", blank=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        if self.end_date == self.initial_date:
            return self.name + " (" + self.initial_date.strftime("%d/%b") + ")"
        else:
            return self.name + " (" + self.initial_date.strftime("%d/%b") + " - " + \
                self.end_date.strftime("%d/%b") + ")"

    def clean(self):
        if not self.name or not self.initial_date or not self.end_date:
            raise ValidationError(_("Every event needs a name, a date of beginning and ending"))
