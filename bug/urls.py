from django.urls import path

from . import views

app_name = 'bug'

urlpatterns = [
    path('add', views.add_bug, name="create_bug"),
    path('list', views.list_bugs, name="list_bugs"),
    path('bug/<int:bug_id>/view', views.detail_bug, name="detail_bug"),
    path('bug/<int:bug_id>/edit', views.update_bug, name="edit_bug"),
]
