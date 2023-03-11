from django.urls import path

from . import views

app_name = 'metrics'

urlpatterns = [
    path('', views.index, name='index'),
    path('ii', views.ii, name='ii'),
    path('activities_plan', views.show_activities_plan, name='show_activities'),
]
