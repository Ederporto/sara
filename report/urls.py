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
    path("add/funding", views.add_funding, name="add_funding"),
    path("add/partner", views.add_partner, name="add_partner"),
    path("add/technology", views.add_technology, name="add_technology"),
]
