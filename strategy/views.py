from django.shortcuts import render
from .models import StrategicAxis


def show_strategy(request):
    strategic_axes = StrategicAxis.objects.all()
    return render(request, "metrics/strategy.html", {"axes": strategic_axes})
