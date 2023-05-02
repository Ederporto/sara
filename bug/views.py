import csv
import datetime
import pandas as pd
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.utils.translation import gettext as _
from django.contrib import messages
from .forms import BugForm, ObservationForm
from .models import Bug, Observation
import zipfile
from io import BytesIO


@permission_required("bug.add_bug")
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


@permission_required("bug.view_bug")
def list_bugs(request):
    bugs = Bug.objects.all()
    context = {"dataset": bugs}
    return render(request, "bug/list_bugs.html", context)


@permission_required("bug.view_bug")
def export_bugs(request):
    buffer = BytesIO()
    zip_file = zipfile.ZipFile(buffer, mode="w")
    posfix = " - {}".format(datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%S'))
    zip_name = _("SARA - Bugs")

    bugs = Bug.objects.all()
    header = [_("ID"), _("Title"), _("Description"), _("Type"), _("Status"), _("Date of report"), _("Reporter"), _("Update date"), _("Observation"), _("Answer date")]
    rows = []

    for bug in bugs:
        try:
            bug_observation = bug.observation
        except Observation.DoesNotExist:
            bug_observation = None

        observation = bug_observation.observation if bug_observation else ""
        date_of_answer = bug_observation.date_of_answer if bug_observation else ""

        rows.append([bug.pk, bug.title, bug.description, bug.type_of_bug, bug.status, bug.date_of_report, bug.reporter_id, bug.update_date, observation, date_of_answer])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    df = df.astype(dtype={_("ID"): int, _("Title"): str, _("Description"): str, _("Type"): int, _("Status"): int, _("Date of report"): "datetime64[ns]", _("Reporter"): int, _("Update date"): "datetime64[ns]", _("Observation"): str, _("Answer date"): "datetime64[ns]"})
    df[_("Date of report")] = df[_("Date of report")].dt.tz_localize(None)
    df[_("Update date")] = df[_("Update date")].dt.tz_localize(None)
    df[_("Answer date")] = df[_("Answer date")].dt.tz_localize(None)

    csv_file = BytesIO()
    df.to_csv(path_or_buf=csv_file, index=False)
    zip_file.writestr("{}.csv".format("Bug report" + posfix), csv_file.getvalue())

    excel_file = BytesIO()
    writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Report", index=False)
    writer.close()
    zip_file.writestr("{}.xlsx".format("Bug report" + posfix), excel_file.getvalue())

    zip_file.close()
    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename=' + zip_name + posfix + '.zip'

    return response


@permission_required("bug.view_bug")
def detail_bug(request, bug_id):
    context = {"data": Bug.objects.get(pk=bug_id)}

    return render(request, "bug/detail_bug.html", context)


@permission_required("bug.change_bug")
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


@permission_required("bug.add_observation")
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


@permission_required("bug.change_observation")
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
