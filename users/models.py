from django.db import models
from django.contrib.auth.admin import User
from django.utils.translation import gettext as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group


class UserProfile(models.Model):
    GENDER_CHOICES = (("M", _("Male")),
                      ("F", _("Female")),
                      ("NB", _("Non Binary")),
                      ("?", _("Other")))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=True, blank=True, default="X")
    professional_wiki_handle = models.CharField(_("WMB username"), max_length=50, null=True, blank=True)
    personal_wiki_handle = models.CharField(_("Wiki username"), max_length=50, null=True, blank=True)
    photograph = models.CharField(_("Photograph"), max_length=420, null=True, blank=True)

    twitter = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)

    wikidata_item = models.CharField(max_length=100, null=True, blank=True)
    linkedin = models.CharField(max_length=100, null=True, blank=True)
    lattes = models.CharField(max_length=100, null=True, blank=True)
    orcid = models.CharField(max_length=100, null=True, blank=True)
    google_scholar = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __str__(self):
        return self.professional_wiki_handle or self.user.first_name

    def clean(self):
        if not self.user or not self.professional_wiki_handle:
            raise ValidationError(_("You need to fill both the user and their wiki handle"))


class TeamArea(models.Model):
    text = models.CharField(max_length=420)
    code = models.CharField(max_length=105)
    manager = models.OneToOneField(UserProfile, on_delete=models.SET_NULL, related_name="manager", null=True, blank=True)

    class Meta:
        verbose_name = _("Team area")
        verbose_name_plural = _("Team areas")

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text:
            raise ValidationError(_("You need to fill the text field"))
        if not self.code:
            raise ValidationError(_("You need to fill the code field"))


class Position(models.Model):
    text = models.CharField(max_length=420)
    type = models.ForeignKey(Group, on_delete=models.CASCADE)
    area_associated = models.ForeignKey(TeamArea, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")

    def __str__(self):
        return self.text


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
