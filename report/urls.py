from django.urls import path
from . import views

app_name = "report"

urlpatterns = [
    path("add", views.add_report, name="add_report"),
    path("list", views.list_reports, name="list_reports"),
    path("<int:report_id>/view", views.detail_report, name="detail_report"),
    path("<int:report_id>/export", views.export_report, name="export_report"),
    path("all/export", views.export_report, name="export_all_reports"),
    path("<int:report_id>/update", views.update_report, name="update_report"),
    path("<int:report_id>/delete", views.delete_report, name="delete_report"),

    path("add/area_activated", views.add_area_activated, name="add_area_activated"),
    path("list/area_activated", views.list_areas, name="list_areas_activated"),
    path("add/funding", views.add_funding, name="add_funding"),
    path("list/fundings", views.list_fundings, name="list_fundings"),
    path("add/partner", views.add_partner, name="add_partner"),
    path("list/partners", views.list_partners, name="list_partners"),
    path("add/technology", views.add_technology, name="add_technology"),
    path("list/technologies", views.list_technologies, name="list_technologies"),

    path("get_activities/", views.get_activities, name="get_activities"),
    path("get_areas/", views.get_areas, name="get_areas"),
    path("get_fundings/", views.get_fundings, name="get_fundings"),
    path("get_partnerships/", views.get_partnerships, name="get_partnerships"),
    path("get_technologies/", views.get_technologies, name="get_tecnologies"),
    path("get_metrics/", views.get_metrics, name="get_metrics"),
    path("get_objectives/", views.get_objectives, name="get_objectives"),
]
