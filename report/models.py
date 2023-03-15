from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.dispatch import receiver
from django.db.models.signals import post_save

from metrics.models import Activity
from users.models import TeamArea, UserProfile
from strategy.models import StrategicAxis, Direction


class Funding(models.Model):
    name = models.CharField(max_length=420)
    value = models.FloatField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = _("Funding")
        verbose_name_plural = _("Fundings")

    def __str__(self):
        return self.name


class Editor(models.Model):
    username = models.CharField(max_length=420)

    class Meta:
        verbose_name = _("Editor")
        verbose_name_plural = _("Editors")

    def __str__(self):
        return self.username


class Partner(models.Model):
    name = models.CharField(max_length=420)
    website = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")

    def __str__(self):
        return self.name


class Organizer(models.Model):
    name = models.CharField(max_length=420)
    institution = models.ManyToManyField(Partner, related_name="organizer_institution")

    class Meta:
        verbose_name = _("Organizer")
        verbose_name_plural = _("Organizers")

    def __str__(self):
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=420)

    class Meta:
        verbose_name = _("Technology")
        verbose_name_plural = _("Technologies")

    def __str__(self):
        return self.name


class AreaActivated (models.Model):
    text = models.TextField(_("Name of the area activated"), max_length=420)
    contact = models.TextField(max_length=420, null=True, blank=True)

    class Meta:
        verbose_name = _("Area activated")
        verbose_name_plural = _("Areas activated")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


@receiver(post_save, sender=TeamArea)
def save_team_area_as_area_activated(sender, instance, created, **kwargs):
    if created:
        contact = ""
        if instance.manager:
            contact = instance.manager.professional_wiki_handle
        AreaActivated.objects.create(text=instance.text, contact=contact)


class LearningArea(models.Model):
    text = models.CharField(max_length=420)

    class Meta:
        verbose_name = _("Learning area")
        verbose_name_plural = _("Learning areas")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class StrategicLearningQuestion(models.Model):
    text = models.CharField(max_length=420)
    learning_area = models.ForeignKey(LearningArea, on_delete=models.CASCADE, null=True, related_name='strategic_question')

    class Meta:
        verbose_name = _("Strategic learning question")
        verbose_name_plural = _("Strategic learning questions")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class EvaluationObjective(models.Model):
    text = models.CharField(max_length=420)
    learning_area_of_objective = models.ForeignKey(LearningArea, on_delete=models.CASCADE, null=True,
                                                   related_name='evaluation_objective')

    class Meta:
        verbose_name = _("Evaluation objective")
        verbose_name_plural = _("Evaluation objectives")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))


class Report(models.Model):
    created_by = models.ForeignKey(UserProfile, on_delete=models.RESTRICT, related_name="user_reporting", null=True)
    modified_by = models.ForeignKey(UserProfile, on_delete=models.RESTRICT, related_name="user_modifying", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    # Administrative fields
    activity_associated = models.ForeignKey(Activity, on_delete=models.RESTRICT, related_name="activity_associated", null=True, blank=True)
    activity_other = models.TextField(max_length=420, blank=True, default="")
    area_responsible = models.ForeignKey(TeamArea, on_delete=models.RESTRICT, related_name="responsible")
    area_activated = models.ManyToManyField(AreaActivated, related_name="area_activated")
    initial_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=420)
    funding_associated = models.ForeignKey(Funding, on_delete=models.RESTRICT, related_name="funding_associated", null=True, blank=True)
    links = models.TextField(max_length=10000)
    public_communication = models.TextField(max_length=10000)

    # Quantitative metrics
    participants = models.IntegerField(null=True, blank=True, default=0)
    resources = models.IntegerField(null=True, blank=True, default=0)
    feedbacks = models.IntegerField(null=True, blank=True, default=0)
    editors = models.ManyToManyField(Editor, related_name="editors", blank=True)
    organizers = models.ManyToManyField(Organizer, related_name="organizers", blank=True)
    partners_activated = models.ManyToManyField(Partner, related_name="partners", blank=True)
    technologies_used = models.ManyToManyField(Technology, related_name="tecnologies", blank=True)

    # Wikimedia projects
    wikipedia_created = models.IntegerField(null=True, blank=True, default=0)
    wikipedia_edited = models.IntegerField(null=True, blank=True, default=0)
    commons_created = models.IntegerField(null=True, blank=True, default=0)
    commons_edited = models.IntegerField(null=True, blank=True, default=0)
    wikidata_created = models.IntegerField(null=True, blank=True, default=0)
    wikidata_edited = models.IntegerField(null=True, blank=True, default=0)
    wikiversity_created = models.IntegerField(null=True, blank=True, default=0)
    wikiversity_edited = models.IntegerField(null=True, blank=True, default=0)
    wikibooks_created = models.IntegerField(null=True, blank=True, default=0)
    wikibooks_edited = models.IntegerField(null=True, blank=True, default=0)
    wikisource_created = models.IntegerField(null=True, blank=True, default=0)
    wikisource_edited = models.IntegerField(null=True, blank=True, default=0)
    wikinews_created = models.IntegerField(null=True, blank=True, default=0)
    wikinews_edited = models.IntegerField(null=True, blank=True, default=0)
    wikiquote_created = models.IntegerField(null=True, blank=True, default=0)
    wikiquote_edited = models.IntegerField(null=True, blank=True, default=0)
    wiktionary_created = models.IntegerField(null=True, blank=True, default=0)
    wiktionary_edited = models.IntegerField(null=True, blank=True, default=0)
    wikivoyage_created = models.IntegerField(null=True, blank=True, default=0)
    wikivoyage_edited = models.IntegerField(null=True, blank=True, default=0)
    wikispecies_created = models.IntegerField(null=True, blank=True, default=0)
    wikispecies_edited = models.IntegerField(null=True, blank=True, default=0)
    metawiki_created = models.IntegerField(null=True, blank=True, default=0)
    metawiki_edited = models.IntegerField(null=True, blank=True, default=0)
    mediawiki_created = models.IntegerField(null=True, blank=True, default=0)
    mediawiki_edited = models.IntegerField(null=True, blank=True, default=0)

    # Strategy
    directions_related = models.ManyToManyField(Direction, related_name="direction_related", blank=True)
    learning = models.TextField(max_length=500, blank=True)

    # Theory of Change
    learning_questions_related = models.ManyToManyField(StrategicLearningQuestion, related_name="strategic_learning_question_related", blank=True)

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.initial_date

        super(Report, self).save(*args, **kwargs)


class EvaluationObjectiveAnswer(models.Model):
    objective = models.ForeignKey(EvaluationObjective, on_delete=models.CASCADE, related_name="answer")
    answer = models.CharField(max_length=4200, null=True, blank=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="evaluation_objective_answer")

    class Meta:
        verbose_name = _("Evaluation objective answer")
        verbose_name_plural = _("Evaluation objective answers")

    def __str__(self):
        return self.objective.text + ": " + self.answer
