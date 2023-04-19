import datetime

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.translation import gettext as _
from django.contrib import messages
from .forms import BugForm, ObservationForm
from .models import Bug, Observation


def add_bug(request):
    if request.method == "POST":
        bug_form = BugForm(request.POST)
        if bug_form.is_valid():
            bug = bug_form.save(commit=False)
            bug.reporter = request.user.userprofile
            bug.save()

            messages.success(request, _("Reported sucessfully!"))
            return redirect(reverse("bug:detail_bug", kwargs={"bug_id": bug.pk}))
        else:
            bug_form = BugForm(request.POST)
            messages.error(request, _("Something went wrong!"))
    else:
        bug_form = BugForm()

    return render(request, "bug/add_bug.html", {"bugform": bug_form})


def list_bugs(request):
    bugs = Bug.objects.all()
    context = {"dataset": bugs}
    return render(request, "bug/list_bugs.html", context)


def detail_bug(request, bug_id):
    context = {"data": Bug.objects.get(pk=bug_id)}

    return render(request, "bug/detail_bug.html", context)


def update_bug(request, bug_id):
    bug = get_object_or_404(Bug, pk=bug_id)

    if request.method == "POST":
        bug_form = BugForm(request.POST, instance=bug)

        if bug_form.is_valid():
            bug = bug_form.save(commit=False)
            bug.update_date = datetime.datetime.today()
            bug.save()
            messages.success(request, _("Changes made successfully!"))

            return redirect(reverse("bug:detail_bug", kwargs={"bug_id": bug_id}))
        else:
            bug_form = BugForm(instance=bug)
            messages.error(request, _("Something went wrong!"))
    else:
        bug_form = BugForm(instance=bug)
    return render(request, "bug/update_bug.html", {"bugform": bug_form})


def add_observation(request, bug_id):
    if request.method == "POST":
        obs_form = ObservationForm(request.POST)
        if obs_form.is_valid():
            obs = obs_form.save(commit=False)
            obs.bug_report = Bug.objects.get(pk=bug_id)
            obs.save()

            messages.success(request, _("Answered sucessfully!"))
            return redirect(reverse("bug:detail_bug", kwargs={"bug_id": bug_id}))
        else:
            obs_form = ObservationForm(request.POST)
            messages.error(request, _("Something went wrong!"))
    else:
        obs_form = ObservationForm()
    return render(request, "bug/add_observation.html", {"obsform": obs_form})


def edit_observation(request, bug_id):
    obs = get_object_or_404(Observation, bug_report=bug_id)

    if request.method == "POST":
        obs_form = ObservationForm(request.POST, instance=obs)

        if obs_form.is_valid():
            obs = obs_form.save(commit=False)
            obs.date_of_answer = datetime.datetime.today()
            obs.save()
            messages.success(request, _("Changes made successfully!"))

            return redirect(reverse("bug:detail_bug", kwargs={"bug_id": bug_id}))
        else:
            obs_form = BugForm(instance=obs)
            messages.error(request, _("Something went wrong!"))
    else:
        obs_form = BugForm(instance=obs)
    return render(request, "bug/update_observation.html", {"obsform": obs_form})
