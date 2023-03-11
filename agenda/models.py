from django.db import models
from users.models import TeamArea
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


# CALENDAR OF EVENTS
class Event(models.Model):
    name = models.CharField(max_length=420)
    initial_date = models.DateField()
    end_date = models.DateField()
    area_responsible = models.ForeignKey(TeamArea, on_delete=models.RESTRICT, related_name="area_responsible")
    area_involved = models.ManyToManyField(TeamArea, related_name="area_involved", blank=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.name + "(" + self.initial_date.strftime("%d/%b") + " - " + self.end_date.strftime("%d/%b") + ")"

    def clean(self):
        if not self.name or not self.initial_date or not self.end_date:
            raise ValidationError(_("Every event needs a name, a date of beginning and ending"))
