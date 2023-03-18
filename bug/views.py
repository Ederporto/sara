import datetime

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.translation import gettext as _
from django.contrib import messages
from users.models import UserProfile
from .forms import BugForm, BugReportForm
from .models import Bug
from django.contrib.auth.models import Permission


def add_bug(request):
    if request.method == "POST":
        bug_form = BugForm(request.POST)

        reporter = get_object_or_404(UserProfile, user=request.user)

        if bug_form.is_valid():
            bug = bug_form.save()

            bug.reporter = reporter
            bug.save()

            messages.success(request, _("Reported sucessfully!"))
        else:
            messages.error(request, _("Something went wrong!"))
        return redirect(reverse("bug:list_bugs"))
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
        if request.user.has_perm("bug.delete_bug"):
            bug_form = BugReportForm(request.POST, instance=bug)
        else:
            bug_form = BugForm(request.POST, instance=bug)

        if bug_form.is_valid():
            bug = bug_form.save()
            bug.update_date = datetime.datetime.today()
            bug.save()
            messages.success(request, _("Changes made successfully!"))

            return redirect(reverse("bug:detail_bug", kwargs={"bug_id": bug_id}))
        else:
            messages.error(request, _("Something went wrong!"))
    else:
        if request.user.has_perm("bug.delete_bug"):
            bug_form = BugReportForm(instance=bug)
        else:
            bug_form = BugForm(instance=bug)
    return render(request, "bug/update_bug.html", {"bugform": bug_form})
