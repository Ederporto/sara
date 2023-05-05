import calendar
from django.shortcuts import render, HttpResponse
from django.db.models import Q, Count, Sum
from .models import Activity, Area, Metric
from report.models import Report, Editor, Organizer, Partner, Project, Funding
from django import template
from django.contrib.auth.decorators import login_required, permission_required
register = template.Library()
import csv
import json

calendar.setfirstweekday(calendar.SUNDAY)


def index(request):
    return render(request, "metrics/home.html")


def about(request):
    return render(request, "metrics/about.html")


def show_activities_plan(request):
    activities = Activity.objects.all()
    project = Project.objects.get(text="Plano de atividades")
    areas = Area.objects.filter(project=project)

    return render(request, "metrics/activities_plan.html", {"areas": areas, "activities": activities})


@login_required
@permission_required("metrics.view_metric")
def show_metrics(request):
    total_sum = get_aggregated_metrics_data()
    total_done = get_aggregated_metrics_data_done()
    timeline_activites = get_activities()

    projects = Project.objects.filter(pk__in=list(Metric.objects.filter(project__isnull=False).values_list("project__pk",flat=True)))
    projects_metrics_sum = []

    if projects.count():
        for project in projects:
            projects_metrics_sum.append({"funding": project.text, "total_sum": get_aggregated_metrics_data(project=project)})

    context = {"total_sum": total_sum, "total_done": total_done, "timeline": timeline_activites, "projects_metrics": projects_metrics_sum}
    return render(request, "metrics/list_metrics.html", context=context)


def get_aggregated_metrics_data(project=None):
    total_sum = {}

    q_filter = Q(project__isnull=True)
    if project:
        q_filter = Q(project=project)

    wikipedia_created = Metric.objects.filter(q_filter).aggregate(Sum('wikipedia_created'))['wikipedia_created__sum'] or 0
    commons_created = Metric.objects.filter(q_filter).aggregate(Sum('commons_created'))['commons_created__sum'] or 0
    wikidata_created = Metric.objects.filter(q_filter).aggregate(Sum('wikidata_created'))['wikidata_created__sum'] or 0
    wikiversity_created = Metric.objects.filter(q_filter).aggregate(Sum('wikiversity_created'))['wikiversity_created__sum'] or 0
    wikibooks_created = Metric.objects.filter(q_filter).aggregate(Sum('wikibooks_created'))['wikibooks_created__sum'] or 0
    wikisource_created = Metric.objects.filter(q_filter).aggregate(Sum('wikisource_created'))['wikisource_created__sum'] or 0
    wikinews_created = Metric.objects.filter(q_filter).aggregate(Sum('wikinews_created'))['wikinews_created__sum'] or 0
    wikiquote_created = Metric.objects.filter(q_filter).aggregate(Sum('wikiquote_created'))['wikiquote_created__sum'] or 0
    wiktionary_created = Metric.objects.filter(q_filter).aggregate(Sum('wiktionary_created'))['wiktionary_created__sum'] or 0
    wikivoyage_created = Metric.objects.filter(q_filter).aggregate(Sum('wikivoyage_created'))['wikivoyage_created__sum'] or 0
    wikispecies_created = Metric.objects.filter(q_filter).aggregate(Sum('wikispecies_created'))['wikispecies_created__sum'] or 0
    metawiki_created = Metric.objects.filter(q_filter).aggregate(Sum('metawiki_created'))['metawiki_created__sum'] or 0
    mediawiki_created = Metric.objects.filter(q_filter).aggregate(Sum('mediawiki_created'))['mediawiki_created__sum'] or 0

    wikipedia_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikipedia_edited'))['wikipedia_edited__sum'] or 0
    commons_edited = Metric.objects.filter(q_filter).aggregate(Sum('commons_edited'))['commons_edited__sum'] or 0
    wikidata_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikidata_edited'))['wikidata_edited__sum'] or 0
    wikiversity_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikiversity_edited'))['wikiversity_edited__sum'] or 0
    wikibooks_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikibooks_edited'))['wikibooks_edited__sum'] or 0
    wikisource_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikisource_edited'))['wikisource_edited__sum'] or 0
    wikinews_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikinews_edited'))['wikinews_edited__sum'] or 0
    wikiquote_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikiquote_edited'))['wikiquote_edited__sum'] or 0
    wiktionary_edited = Metric.objects.filter(q_filter).aggregate(Sum('wiktionary_edited'))['wiktionary_edited__sum'] or 0
    wikivoyage_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikivoyage_edited'))['wikivoyage_edited__sum'] or 0
    wikispecies_edited = Metric.objects.filter(q_filter).aggregate(Sum('wikispecies_edited'))['wikispecies_edited__sum'] or 0
    metawiki_edited = Metric.objects.filter(q_filter).aggregate(Sum('metawiki_edited'))['metawiki_edited__sum'] or 0
    mediawiki_edited = Metric.objects.filter(q_filter).aggregate(Sum('mediawiki_edited'))['mediawiki_edited__sum'] or 0

    number_of_participants = Metric.objects.filter(q_filter).aggregate(Sum('number_of_participants'))['number_of_participants__sum'] or 0
    number_of_resources = Metric.objects.filter(q_filter).aggregate(Sum('number_of_resources'))['number_of_resources__sum'] or 0
    number_of_feedbacks = Metric.objects.filter(q_filter).aggregate(Sum('number_of_feedbacks'))['number_of_feedbacks__sum'] or 0
    number_of_editors = Metric.objects.filter(q_filter).aggregate(Sum('number_of_editors'))['number_of_editors__sum'] or 0
    number_of_organizers = Metric.objects.filter(q_filter).aggregate(Sum('number_of_organizers'))['number_of_organizers__sum'] or 0
    number_of_partnerships = Metric.objects.filter(q_filter).aggregate(Sum('number_of_partnerships'))['number_of_partnerships__sum'] or 0

    number_of_retained_editors = Metric.objects.filter(q_filter).filter(other_type="retained").aggregate(Sum('number_of_editors'))['number_of_editors__sum'] or 0
    number_of_retained_organizers = Metric.objects.filter(q_filter).filter(other_type="retained").aggregate(Sum('number_of_organizers'))['number_of_organizers__sum'] or 0
    number_of_retained_partnerships = Metric.objects.filter(q_filter).filter(other_type="retained").aggregate(Sum('number_of_partnerships'))['number_of_partnerships__sum'] or 0

    total_sum["wikipedia_created"] = wikipedia_created
    total_sum["commons_created"] = commons_created
    total_sum["wikidata_created"] = wikidata_created
    total_sum["wikiversity_created"] = wikiversity_created
    total_sum["wikibooks_created"] = wikibooks_created
    total_sum["wikisource_created"] = wikisource_created
    total_sum["wikinews_created"] = wikinews_created
    total_sum["wikiquote_created"] = wikiquote_created
    total_sum["wiktionary_created"] = wiktionary_created
    total_sum["wikivoyage_created"] = wikivoyage_created
    total_sum["wikispecies_created"] = wikispecies_created
    total_sum["metawiki_created"] = metawiki_created
    total_sum["mediawiki_created"] = mediawiki_created

    total_sum["wikipedia_edited"] = wikipedia_edited
    total_sum["commons_edited"] = commons_edited
    total_sum["wikidata_edited"] = wikidata_edited
    total_sum["wikiversity_edited"] = wikiversity_edited
    total_sum["wikibooks_edited"] = wikibooks_edited
    total_sum["wikisource_edited"] = wikisource_edited
    total_sum["wikinews_edited"] = wikinews_edited
    total_sum["wikiquote_edited"] = wikiquote_edited
    total_sum["wiktionary_edited"] = wiktionary_edited
    total_sum["wikivoyage_edited"] = wikivoyage_edited
    total_sum["wikispecies_edited"] = wikispecies_edited
    total_sum["metawiki_edited"] = metawiki_edited
    total_sum["mediawiki_edited"] = mediawiki_edited

    total_sum["participants"] = number_of_participants
    total_sum["resources"] = number_of_resources
    total_sum["feedbacks"] = number_of_feedbacks
    total_sum["editors"] = number_of_editors
    total_sum["organizers"] = number_of_organizers
    total_sum["partnerships"] = number_of_partnerships
    total_sum["retained_editors"] = number_of_retained_editors
    total_sum["retained_organizers"] = number_of_retained_organizers
    total_sum["retained_partnerships"] = number_of_retained_partnerships

    return total_sum


def get_aggregated_metrics_data_done():
    total_sum = {}
    wikipedia_created = Report.objects.aggregate(Sum('wikipedia_created'))['wikipedia_created__sum']
    commons_created = Report.objects.aggregate(Sum('commons_created'))['commons_created__sum']
    wikidata_created = Report.objects.aggregate(Sum('wikidata_created'))['wikidata_created__sum']
    wikiversity_created = Report.objects.aggregate(Sum('wikiversity_created'))['wikiversity_created__sum']
    wikibooks_created = Report.objects.aggregate(Sum('wikibooks_created'))['wikibooks_created__sum']
    wikisource_created = Report.objects.aggregate(Sum('wikisource_created'))['wikisource_created__sum']
    wikinews_created = Report.objects.aggregate(Sum('wikinews_created'))['wikinews_created__sum']
    wikiquote_created = Report.objects.aggregate(Sum('wikiquote_created'))['wikiquote_created__sum']
    wiktionary_created = Report.objects.aggregate(Sum('wiktionary_created'))['wiktionary_created__sum']
    wikivoyage_created = Report.objects.aggregate(Sum('wikivoyage_created'))['wikivoyage_created__sum']
    wikispecies_created = Report.objects.aggregate(Sum('wikispecies_created'))['wikispecies_created__sum']
    metawiki_created = Report.objects.aggregate(Sum('metawiki_created'))['metawiki_created__sum']
    mediawiki_created = Report.objects.aggregate(Sum('mediawiki_created'))['mediawiki_created__sum']

    wikipedia_edited = Report.objects.aggregate(Sum('wikipedia_edited'))['wikipedia_edited__sum']
    commons_edited = Report.objects.aggregate(Sum('commons_edited'))['commons_edited__sum']
    wikidata_edited = Report.objects.aggregate(Sum('wikidata_edited'))['wikidata_edited__sum']
    wikiversity_edited = Report.objects.aggregate(Sum('wikiversity_edited'))['wikiversity_edited__sum']
    wikibooks_edited = Report.objects.aggregate(Sum('wikibooks_edited'))['wikibooks_edited__sum']
    wikisource_edited = Report.objects.aggregate(Sum('wikisource_edited'))['wikisource_edited__sum']
    wikinews_edited = Report.objects.aggregate(Sum('wikinews_edited'))['wikinews_edited__sum']
    wikiquote_edited = Report.objects.aggregate(Sum('wikiquote_edited'))['wikiquote_edited__sum']
    wiktionary_edited = Report.objects.aggregate(Sum('wiktionary_edited'))['wiktionary_edited__sum']
    wikivoyage_edited = Report.objects.aggregate(Sum('wikivoyage_edited'))['wikivoyage_edited__sum']
    wikispecies_edited = Report.objects.aggregate(Sum('wikispecies_edited'))['wikispecies_edited__sum']
    metawiki_edited = Report.objects.aggregate(Sum('metawiki_edited'))['metawiki_edited__sum']
    mediawiki_edited = Report.objects.aggregate(Sum('mediawiki_edited'))['mediawiki_edited__sum']

    number_of_participants = Report.objects.aggregate(Sum('participants'))['participants__sum']
    number_of_resources = Report.objects.aggregate(Sum('resources'))['resources__sum']
    number_of_feedbacks = Report.objects.aggregate(Sum('feedbacks'))['feedbacks__sum']
    number_of_editors = Report.objects.annotate(num_editors=Count('editors')).aggregate(Sum('num_editors'))['num_editors__sum']
    number_of_organizers = Report.objects.annotate(num_organizers=Count('organizers')).aggregate(Sum('num_organizers'))['num_organizers__sum']
    number_of_partnerships = Report.objects.annotate(num_partnerships=Count('partners_activated')).aggregate(Sum('num_partnerships'))['num_partnerships__sum']

    editors_in_more_than_one_activity = Editor.objects.annotate(report_count=Count('editors')).filter(report_count__gt=1)
    organizers_in_more_than_one_activity = Organizer.objects.annotate(report_count=Count('organizers')).filter(report_count__gt=1)
    partners_in_more_than_one_activity = Partner.objects.annotate(report_count=Count('partners')).filter(report_count__gt=1)

    total_sum["wikipedia_created"] = wikipedia_created
    total_sum["commons_created"] = commons_created
    total_sum["wikidata_created"] = wikidata_created
    total_sum["wikiversity_created"] = wikiversity_created
    total_sum["wikibooks_created"] = wikibooks_created
    total_sum["wikisource_created"] = wikisource_created
    total_sum["wikinews_created"] = wikinews_created
    total_sum["wikiquote_created"] = wikiquote_created
    total_sum["wiktionary_created"] = wiktionary_created
    total_sum["wikivoyage_created"] = wikivoyage_created
    total_sum["wikispecies_created"] = wikispecies_created
    total_sum["metawiki_created"] = metawiki_created
    total_sum["mediawiki_created"] = mediawiki_created

    total_sum["wikipedia_edited"] = wikipedia_edited
    total_sum["commons_edited"] = commons_edited
    total_sum["wikidata_edited"] = wikidata_edited
    total_sum["wikiversity_edited"] = wikiversity_edited
    total_sum["wikibooks_edited"] = wikibooks_edited
    total_sum["wikisource_edited"] = wikisource_edited
    total_sum["wikinews_edited"] = wikinews_edited
    total_sum["wikiquote_edited"] = wikiquote_edited
    total_sum["wiktionary_edited"] = wiktionary_edited
    total_sum["wikivoyage_edited"] = wikivoyage_edited
    total_sum["wikispecies_edited"] = wikispecies_edited
    total_sum["metawiki_edited"] = metawiki_edited
    total_sum["mediawiki_edited"] = mediawiki_edited

    total_sum["participants"] = number_of_participants
    total_sum["resources"] = number_of_resources
    total_sum["feedbacks"] = number_of_feedbacks
    total_sum["editors"] = number_of_editors
    total_sum["organizers"] = number_of_organizers
    total_sum["partnerships"] = number_of_partnerships

    total_sum["retained_editors"] = editors_in_more_than_one_activity.count()
    total_sum["retained_organizers"] = organizers_in_more_than_one_activity.count()
    total_sum["retained_partnerships"] = partners_in_more_than_one_activity.count()

    return total_sum


def get_activities():
    activities = Report.objects.all().order_by("end_date")
    chart_data = {}
    chart_data["wikipedia"] = get_chart_data(activities, "wikipedia_created", "wikipedia_edited")
    chart_data["commons"] = get_chart_data(activities, "commons_created", "commons_edited")
    chart_data["wikidata"] = get_chart_data(activities, "wikidata_created", "wikidata_edited")
    chart_data["wikiversity"] = get_chart_data(activities, "wikiversity_created", "wikiversity_edited")
    chart_data["wikibooks"] = get_chart_data(activities, "wikibooks_created", "wikibooks_edited")
    chart_data["wikisource"] = get_chart_data(activities, "wikisource_created", "wikisource_edited")
    chart_data["wikinews"] = get_chart_data(activities, "wikinews_created", "wikinews_edited")
    chart_data["wikiquote"] = get_chart_data(activities, "wikiquote_created", "wikiquote_edited")
    chart_data["wiktionary"] = get_chart_data(activities, "wiktionary_created", "wiktionary_edited")
    chart_data["wikivoyage"] = get_chart_data(activities, "wikivoyage_created", "wikivoyage_edited")
    chart_data["wikispecies"] = get_chart_data(activities, "wikispecies_created", "wikispecies_edited")
    chart_data["metawiki"] = get_chart_data(activities, "metawiki_created", "metawiki_edited")
    chart_data["mediawiki"] = get_chart_data(activities, "mediawiki_created", "mediawiki_edited")

    chart_data["participants"] = get_chart_data(activities, "participants", "participants")
    chart_data["resources"] = get_chart_data(activities, "resources", "resources")
    chart_data["feedbacks"] = get_chart_data(activities, "feedbacks", "feedbacks")
    chart_data["editors"] = get_chart_data_many_to_many(activities, "editors")
    chart_data["organizers"] = get_chart_data_many_to_many(activities, "organizers")
    chart_data["partnerships"] = get_chart_data_many_to_many(activities, "partners_activated")

    return chart_data


def get_chart_data(activities, created_field, edited_field):
    filtered_activities = activities.filter(Q(**{created_field + '__gt': 0}) | Q(**{edited_field + '__gt': 0})).order_by("end_date")
    chart_data = []
    total_ = 0
    for activity in filtered_activities:
        total_ += getattr(activity, created_field) + getattr(activity, edited_field)
        chart_data.append({"x": activity.end_date.isoformat(), "y": total_, "label": activity.description})
    return chart_data


def get_chart_data_many_to_many(activities, field):
    filtered_activities = Report.objects.filter(Q(**{field + '__isnull': False})).distinct().order_by("end_date")
    chart_data = []
    total_ = 0
    for activity in filtered_activities:
        total_ += getattr(activity, field).count()
        chart_data.append({"x": activity.end_date.isoformat(), "y": total_, "label": activity.description})
    return chart_data
