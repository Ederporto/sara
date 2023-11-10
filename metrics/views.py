import calendar
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count, Sum, F
from .models import Activity, Area, Metric
from report.models import Report, Editor, Organizer, Partner, Project, Funding
from django import template
from django.contrib.auth.decorators import login_required, permission_required
register = template.Library()
import csv
import json

calendar.setfirstweekday(calendar.SUNDAY)


def index(request):
    context = {"title": _("Home")}
    return render(request, "metrics/home.html", context)


def about(request):
    context = {"title": _("About")}
    return render(request, "metrics/about.html", context)


def show_activities_plan(request):
    activities = Activity.objects.all()
    project = Project.objects.get(pk=1)
    areas = Area.objects.filter(project=project).order_by("id")

    context = {"areas": areas, "activities": activities, "title": _("Activities plan")}

    return render(request, "metrics/activities_plan.html", context)


@login_required
@permission_required("metrics.view_metric")
def show_metrics(request):
    total_sum = get_aggregated_metrics_data()
    total_done = get_aggregated_metrics_data_done()
    timeline_activites = get_activities()

    projects = Project.objects.filter(pk__in=list(Metric.objects.filter(project__isnull=False).values_list("project__pk", flat=True))).exclude(pk=1)
    projects_metrics_sum = []

    if projects.count():
        for project in projects:
            projects_metrics_sum.append({"funding": project.text, "total_sum": get_aggregated_metrics_data(project=project)})

    context = {"total_sum": total_sum, "total_done": total_done, "timeline": timeline_activites, "projects_metrics": projects_metrics_sum, "title": _("Show general metrics")}
    return render(request, "metrics/list_metrics.html", context)


@login_required
@permission_required("metrics.view_metric")
def show_metrics_per_project(request):
    context = {"dataset": get_metrics_and_aggregate_per_project(), "title": _("Show metrics per project")}
    return render(request, "metrics/list_metrics_per_project.html", context)


def get_metrics_and_aggregate_per_project():
    aggregated_metrics_and_results = {}

    for project in Project.objects.all():
        project_metrics = []
        for activity in Activity.objects.filter(area__project=project):
            activity_metrics = {}
            if activity.id != 1:
                q_filter = Q(project=project, activity=activity)
            else:
                q_filter = Q(project=project)
            for metric in Metric.objects.filter(q_filter):
                goal, done = get_goal_and_done_for_metric(metric)

                result_metrics = {key: {"goal": value, "done": done[key]} for key, value in goal.items() if value != 0}
                activity_metrics[metric.id] = {
                    "title": metric.text,
                    "metrics": result_metrics if result_metrics else {"Other metric": {"goal": "-", "done": "-"}}
                }

            if activity_metrics:
                project_metrics.append({
                    "activity": activity.text,
                    "activity_id": activity.id,
                    "activity_metrics": activity_metrics
                })

        if project_metrics:
            aggregated_metrics_and_results[project.id] = {
                "project": project.text,
                "project_metrics": project_metrics
            }
    return aggregated_metrics_and_results


def get_goal_and_done_for_metric(metric):
    reports = Report.objects.filter(metrics_related__in=[metric])
    goal = get_goal_for_metric(metric)
    done = get_done_for_report(reports)

    return goal, done


def get_goal_for_metric(metric):
    return {
        "Wikipedia": metric.wikipedia_created + metric.wikipedia_edited,
        "Wikimedia Commons": metric.commons_created + metric.commons_edited,
        "Wikidata": metric.wikidata_created + metric.wikidata_edited,
        "Wikiversity": metric.wikiversity_created + metric.wikiversity_edited,
        "Wikibooks": metric.wikibooks_created + metric.wikibooks_edited,
        "Wikisource": metric.wikisource_created + metric.wikisource_edited,
        "Wikinews": metric.wikinews_created + metric.wikinews_edited,
        "Wikiquote": metric.wikiquote_created + metric.wikiquote_edited,
        "Wiktionary": metric.wiktionary_created + metric.wiktionary_edited,
        "Wikivoyage": metric.wikivoyage_created + metric.wikivoyage_edited,
        "Wikispecies": metric.wikispecies_created + metric.wikispecies_edited,
        "MetaWiki": metric.metawiki_created + metric.metawiki_edited,
        "MediaWiki": metric.mediawiki_created + metric.mediawiki_edited,
        "Number of participants": metric.number_of_participants,
        "Number of resources": metric.number_of_resources,
        "Number of feedbacks": metric.number_of_feedbacks,
        "Number of events": metric.number_of_events,
        "Number of editors": metric.number_of_editors,
        "Number of editors retained": metric.number_of_editors_retained,
        "Number of new editors": metric.number_of_new_editors,
        "Number of partnerships": metric.number_of_partnerships,
        "Number of organizers": metric.number_of_organizers,
        "Number of organizers retained": metric.number_of_organizers_retained,
        "Number of people reached through social media": metric.number_of_people_reached_through_social_media,
        "Occurence": metric.boolean_type,
    }


def get_done_for_report(reports):
    return {
        "Wikipedia": reports.aggregate(total=Sum(F("wikipedia_created") + F("wikipedia_edited")))["total"] or 0,
        "Wikimedia Commons": reports.aggregate(total=Sum(F("commons_created") + F("commons_edited")))["total"] or 0,
        "Wikidata": reports.aggregate(total=Sum(F("wikidata_created") + F("wikidata_edited")))["total"] or 0,
        "Wikiversity": reports.aggregate(total=Sum(F("wikiversity_created") + F("wikiversity_edited")))["total"] or 0,
        "Wikibooks": reports.aggregate(total=Sum(F("wikibooks_created") + F("wikibooks_edited")))["total"] or 0,
        "Wikisource": reports.aggregate(total=Sum(F("wikisource_created") + F("wikisource_edited")))["total"] or 0,
        "Wikinews": reports.aggregate(total=Sum(F("wikinews_created") + F("wikinews_edited")))["total"] or 0,
        "Wikiquote": reports.aggregate(total=Sum(F("wikiquote_created") + F("wikiquote_edited")))["total"] or 0,
        "Wiktionary": reports.aggregate(total=Sum(F("wiktionary_created") + F("wiktionary_edited")))["total"] or 0,
        "Wikivoyage": reports.aggregate(total=Sum(F("wikivoyage_created") + F("wikivoyage_edited")))["total"] or 0,
        "Wikispecies": reports.aggregate(total=Sum(F("wikispecies_created") + F("wikispecies_edited")))["total"] or 0,
        "MetaWiki": reports.aggregate(total=Sum(F("metawiki_created") + F("metawiki_edited")))["total"] or 0,
        "MediaWiki": reports.aggregate(total=Sum(F("mediawiki_created") + F("mediawiki_edited")))["total"] or 0,
        "Number of participants": reports.aggregate(total=Sum("participants"))["total"] or 0,
        "Number of resources": reports.aggregate(total=Sum("resources"))["total"] or 0,
        "Number of feedbacks": reports.aggregate(total=Sum("feedbacks"))["total"] or 0,
        "Number of events": reports.count() or 0,
        "Number of editors": Editor.objects.filter(editors__in=reports).distinct().count() or 0,
        "Number of editors retained": Editor.objects.filter(retained=True, editors__in=reports).distinct().count() or 0,
        "Number of new editors": Editor.objects.filter(editors__in=reports, account_creation_date__gte=F('editors__initial_date')).count() or 0,
        "Number of partnerships": Partner.objects.filter(partners__in=reports).distinct().count() or 0,
        "Number of organizers": Organizer.objects.filter(organizers__in=reports).distinct().count() or 0,
        "Number of organizers retained": Organizer.objects.filter(retained=True, organizers__in=reports).distinct().count() or 0,
        "Number of people reached through social media": reports.aggregate(total=Sum(F("number_of_people_reached_through_social_media")))["total"] or 0,
        "Occurence": reports.filter(metrics_related__boolean_type=True).exists() or False,
    }


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

    chart_data["participants"] = get_chart_data(activities, "participants")
    chart_data["resources"] = get_chart_data(activities, "resources")
    chart_data["feedbacks"] = get_chart_data(activities, "feedbacks")
    chart_data["editors"] = get_chart_data_many_to_many(activities, "editors")
    chart_data["organizers"] = get_chart_data_many_to_many(activities, "organizers")
    chart_data["partnerships"] = get_chart_data_many_to_many(activities, "partners_activated")

    return chart_data


def get_chart_data(activities, created_field=None, edited_field=None):
    created_filter = Q(**{created_field + '__gt': 0}) if created_field else Q()
    edited_filter = Q(**{edited_field + '__gt': 0}) if edited_field else Q()
    filtered_activities = activities.filter(created_filter | edited_filter).order_by("end_date")
    chart_data = []
    total_ = 0
    for activity in filtered_activities:
        total_created = getattr(activity, created_field) if created_field else 0
        total_edited = getattr(activity, edited_field) if edited_field else 0
        total_ += total_created + total_edited
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


def update_metrics_relations(request):
    main_funding = Project.objects.get(text="Wikimedia Community Fund")
    editors_metrics = Metric.objects.filter(project=main_funding).filter(Q(number_of_editors__gt=0) | Q(number_of_editors_retained__gt=0) | Q(number_of_new_editors__gt=0))
    reports = Report.objects.filter(Q(metrics_related__number_of_editors__gt=0))
    for report in reports:
        report.metrics_related.add(*editors_metrics)
        report.save()

    return redirect(reverse("metrics:per_project"))


@login_required
@permission_required("metrics.view_metric")
def metrics_reports(request, metric_id):
    try:
        metric = Metric.objects.get(pk=metric_id)
        reports = Report.objects.filter(metrics_related=metric_id).order_by("pk")

        goals = get_goal_for_metric(metric)
        filtered_goals = {key: value for key, value in goals.items() if goals[key] > 0}

        values = []
        for goal_key, goal_value in filtered_goals.items():
            report_values = []
            for report in reports:
                done = get_done_for_report(Report.objects.filter(pk=report.id))
                report_values.append({
                    "id": report.id,
                    "description": report.description,
                    "initial_date": report.initial_date,
                    "end_date": report.end_date,
                    "done": done[goal_key],
                })
            values.append({
                "text": goal_key,
                "goal": goal_value,
                "done": sum([report_aux["done"] for report_aux in report_values]),
                "reports": report_values
            })

        context = {"metric": metric, "values": values}

        return render(request, "metrics/list_metrics_reports.html", context)
    except ObjectDoesNotExist:
        return redirect(reverse('metrics:per_project'))

