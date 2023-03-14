from django.urls import path

from . import views

app_name = 'metrics'

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('activities_plan', views.show_activities_plan, name='show_activities'),
]
