from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from users.models import UserProfile
from strategy.models import StrategicAxis


class Project(models.Model):
    text = models.CharField(max_length=420)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class Area(models.Model):
    text = models.CharField(max_length=420)
    related_axis = models.ManyToManyField(StrategicAxis, related_name='areas')
    project = models.ManyToManyField(Project, related_name="project_activity", blank=True)

    class Meta:
        verbose_name = _("Area")
        verbose_name_plural = _("Areas")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class Objective(models.Model):
    text = models.CharField(max_length=420)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='objectives', null=True)

    class Meta:
        verbose_name = _("Objective")
        verbose_name_plural = _("Objectives")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class Activity(models.Model):
    text = models.CharField(max_length=420)
    code = models.CharField(max_length=10, null=True)
    area = models.ForeignKey(Area, on_delete=models.RESTRICT, related_name='activities', null=True)

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class Metric(models.Model):
    text = models.CharField(max_length=420)

    # Projects
    wikipedia_created = models.IntegerField(null=True, default=0)
    wikipedia_edited = models.IntegerField(null=True, default=0)
    commons_created = models.IntegerField(null=True, default=0)
    commons_edited = models.IntegerField(null=True, default=0)
    wikidata_created = models.IntegerField(null=True, default=0)
    wikidata_edited = models.IntegerField(null=True, default=0)
    wikiversity_created = models.IntegerField(null=True, default=0)
    wikiversity_edited = models.IntegerField(null=True, default=0)
    wikibooks_created = models.IntegerField(null=True, default=0)
    wikibooks_edited = models.IntegerField(null=True, default=0)
    wikisource_created = models.IntegerField(null=True, default=0)
    wikisource_edited = models.IntegerField(null=True, default=0)
    wikinews_created = models.IntegerField(null=True, default=0)
    wikinews_edited = models.IntegerField(null=True, default=0)
    wikiquote_created = models.IntegerField(null=True, default=0)
    wikiquote_edited = models.IntegerField(null=True, default=0)
    wiktionary_created = models.IntegerField(null=True, default=0)
    wiktionary_edited = models.IntegerField(null=True, default=0)
    wikivoyage_created = models.IntegerField(null=True, default=0)
    wikivoyage_edited = models.IntegerField(null=True, default=0)
    wikispecies_created = models.IntegerField(null=True, default=0)
    wikispecies_edited = models.IntegerField(null=True, default=0)
    metawiki_created = models.IntegerField(null=True, default=0)
    metawiki_edited = models.IntegerField(null=True, default=0)
    mediawiki_created = models.IntegerField(null=True, default=0)
    mediawiki_edited = models.IntegerField(null=True, default=0)

    # General
    number_of_editors = models.IntegerField(null=True, default=0)
    number_of_editors_retained = models.IntegerField(null=True, default=0)
    number_of_new_editors = models.IntegerField(null=True, default=0)
    number_of_participants = models.IntegerField(null=True, default=0)
    number_of_partnerships = models.IntegerField(null=True, default=0)
    number_of_organizers = models.IntegerField(null=True, default=0)
    number_of_organizers_retained = models.IntegerField(null=True, default=0)
    number_of_resources = models.IntegerField(null=True, default=0)
    number_of_feedbacks = models.IntegerField(null=True, default=0)
    number_of_events = models.IntegerField(null=True, default=0)
    number_of_people_reached_through_social_media = models.IntegerField(null=True, default=0)

    other_type = models.CharField(null=True, blank=True, max_length=420)
    observation = models.CharField(null=True, blank=True, max_length=420)

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="metrics")
    project = models.ManyToManyField(Project, related_name="project_associated", blank=True)

    class Meta:
        verbose_name = _("Metric")
        verbose_name_plural = _("Metrics")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))
