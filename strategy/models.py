from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


class StrategicAxis(models.Model):
    text = models.CharField(max_length=420)
    intentionality = models.CharField(max_length=420, null=True, blank=True)

    class Meta:
        verbose_name = _("Strategic axis")
        verbose_name_plural = _("Strategic axes")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class Direction(models.Model):
    text = models.CharField(max_length=420)
    strategic_axis = models.ForeignKey(StrategicAxis, on_delete=models.CASCADE, related_name='directions')

    class Meta:
        verbose_name = _("Direction")
        verbose_name_plural = _("Directions")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))
