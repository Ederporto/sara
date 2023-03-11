import calendar
from django.shortcuts import render
from .models import Activity, Area
from django import template
register = template.Library()
import csv

calendar.setfirstweekday(calendar.SUNDAY)


def index(request):
    return render(request, "metrics/home.html")


def show_activities_plan(request):
    activities = Activity.objects.all()
    areas = Area.objects.all()

    return render(request, "metrics/activities_plan.html", {"areas": areas, "activities": activities})


def ii(request):
    file = open("file.csv", "r")
    csv_writer = csv.reader(file, delimiter="\n")
    csv_list = [x[0] for x in csv_writer]
    return render(request, "metrics/ii.html", {"csv_file": list(csv_list)})
