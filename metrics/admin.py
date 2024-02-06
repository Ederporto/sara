from django.contrib import admin
from .models import Objective, Area, Activity, Metric, Project

admin.site.register(Project)
admin.site.register(Area)
admin.site.register(Objective)
admin.site.register(Activity)
admin.site.register(Metric)