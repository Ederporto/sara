from django.shortcuts import render
from .models import StrategicAxis
from django.utils.translation import gettext as _


def show_strategy(request):
    strategic_axes = StrategicAxis.objects.all().order_by("id")
    context = {"axes": strategic_axes, "title": _("Strategy")}
    return render(request, "metrics/strategy.html", context)
