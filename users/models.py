from django.db import models
from django.contrib.auth.admin import User
from django.utils.translation import gettext as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    GENDER_CHOICES = (("M", _("Male")),
                      ("F", _("Female")),
                      ("NB", _("Non Binary")),
                      ("?", _("Other")))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, null=True, blank=True, default="X")
    wiki_handle = models.CharField(max_length=50, null=True, blank=True)

    twitter = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)

    linkedin = models.CharField(max_length=100, null=True, blank=True)
    lattes = models.CharField(max_length=100, null=True, blank=True)
    orcid = models.CharField(max_length=100, null=True, blank=True)
    google_scholar = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __str__(self):
        return self.wiki_handle or self.user.first_name

    def clean(self):
        if not self.user or not self.wiki_handle:
            raise ValidationError(_("You need to fill both the user and their wiki_handle"))


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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)