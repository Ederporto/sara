from django.urls import path, re_path

from agenda import views

app_name = 'agenda'

urlpatterns = [
    path('', views.show_calendar, name='show_calendar'),
    path('day', views.show_calendar_day, name='show_calendar_day'),
    path('add', views.add_event, name="create_event"),
    path('list', views.list_events, name="list_events"),
    path('activity/<int:event_id>/delete', views.delete_event, name="delete_event"),
    path('activity/<int:event_id>/edit', views.update_event, name="edit_event"),
    re_path(r'^(?P<year>20\d{2})/(?P<month>(0?[1-9]|1[012]))$',views.show_specific_calendar, name='show_specific_calendar'),
    re_path(r'^(?P<year>20\d{2})/(?P<month>(0?[1-9]|1[012]))/(?P<day>(3[01]|[12][0-9]|0?[1-9]))$',views.show_specific_calendar_day, name='show_specific_calendar_day')
]