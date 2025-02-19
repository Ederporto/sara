from django.shortcuts import redirect
from django.conf import settings

def show_strategy(request):
    return redirect(settings.STRATEGY_URL)
