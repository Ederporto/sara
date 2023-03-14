import calendar
from django.shortcuts import render
from .models import Activity, Area
from django import template
register = template.Library()
import csv

calendar.setfirstweekday(calendar.SUNDAY)


def index(request):
    return render(request, "metrics/home.html")


def about(request):
    return render(request, "metrics/about.html")


def show_activities_plan(request):
    activities = Activity.objects.all()
    areas = Area.objects.all()

    return render(request, "metrics/activities_plan.html", {"areas": areas, "activities": activities})
