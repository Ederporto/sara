from django.shortcuts import render
from .models import StrategicAxis


def show_strategy(request):
    """
    View of the strategic axis and respective action points
    :param request:
    :return: rendering template learning.html which shows a list of
    """

    strategic_axes = StrategicAxis.objects.all()
    return render(request, "metrics/strategy.html", {"axes": strategic_axes})
