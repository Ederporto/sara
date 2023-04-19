import calendar
import datetime
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from .forms import EventForm
from .models import Event


# MONTH CALENDAR
@login_required
def show_calendar(request):
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year

    return redirect('agenda:show_specific_calendar', year=year, month=month)


@login_required
def show_specific_calendar(request, year, month):
    user = request.user
    username = user.first_name if user else "None"

    days_month = days_of_the_month(int(year), int(month))
    month_name = _(calendar.month_name[int(month)])

    context = {"username": username, "calendar": days_month, "month": month, "month_name": month_name, "year": year}
    return render(request, "agenda/calendar.html", context)


# DAY CALENDAR
@login_required
def show_calendar_day(request):
    day = datetime.datetime.now().day
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year

    return redirect("agenda:show_specific_calendar_day", year=year, month=month, day=day)


@login_required
def show_specific_calendar_day(request, year, month, day):
    day_aux = day
    month_aux = month
    year_aux = year
    month_name = _(calendar.month_name[int(month)])

    context = {"month_name": month_name, "year": year_aux, "month": month_aux, "day": day_aux}
    return render(request, "agenda/calendar_day.html", context)


def days_of_the_month(year, month):
    return calendar.monthcalendar(int(year), int(month))


@login_required
@transaction.atomic
def add_event(request):
    form_valid_message = _("Changes done successfully!")
    form_invalid_message = _("Something went wrong!")

    if request.method == "POST":
        event_form = EventForm(request.POST)

        if event_form.is_valid():
            event_form.save()

            messages.success(request, form_valid_message)
            return redirect(reverse("agenda:list_events"))
        else:
            messages.error(request, form_invalid_message)

    else:
        event_form = EventForm()

    return render(request, "agenda/add_event.html", {"eventform": event_form})


@login_required
@transaction.atomic
def list_events(request):
    events = Event.objects.all()
    context = {"dataset": events}
    return render(request, "agenda/list_events.html", context)


@login_required
@transaction.atomic
def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    context = {"event": event}

    if request.method == "POST":
        event.delete()
        return redirect(reverse('agenda:list_events'))

    return render(request, 'agenda/delete_event.html', context)


@login_required
@transaction.atomic
def update_event(request, event_id):
    form_valid_message = _("Changes done successfully!")
    form_invalid_message = _("Something went wrong!")
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        event_form = EventForm(request.POST or None, instance=event)
        year = datetime.datetime.today().year
        month = datetime.datetime.today().month

        if event_form.is_valid():
            event_form.save()
            messages.success(request, form_valid_message)
            year = event_form.instance.initial_date.year
            month = event_form.instance.initial_date.month
        else:
            messages.error(request, form_invalid_message)

        return redirect("agenda:show_specific_calendar", year=year, month=month)
    else:
        event_form = EventForm(instance=event)
    return render(request, "agenda/update_event.html", {"eventform": event_form, "event_id": event.id})
