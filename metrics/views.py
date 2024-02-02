import calendar
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count, Sum, F
from .models import Activity, Area, Metric
from report.models import Report, Editor, Organizer, Partner, Project, Funding
from django import template
from django.conf import settings
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
    # activities = Activity.objects.all()
    # project = Project.objects.filter(current_poa=True).first()
    # areas = Area.objects.filter(project=project).order_by("id")
    #
    # context = {"areas": areas, "activities": activities, "title": _("Activities plan")}
    #
    # return render(request, "metrics/activities_plan.html", context)
    return redirect(settings.POA_URL)


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
        "Number of partnerships activated": metric.number_of_partnerships_activated,
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
        # "Number of resources": reports.aggregate(total=Sum("resources"))["total"] or 0,
        "Number of feedbacks": reports.aggregate(total=Sum("feedbacks"))["total"] or 0,
        "Number of events": reports.count() or 0,
        "Number of editors": Editor.objects.filter(editors__in=reports).distinct().count() or 0,
        "Number of editors retained": Editor.objects.filter(retained=True, editors__in=reports).distinct().count() or 0,
        "Number of new editors": Editor.objects.filter(editors__in=reports, account_creation_date__gte=F('editors__initial_date')).count() or 0,
        "Number of partnerships activated": Partner.objects.filter(partners__in=reports).distinct().count() or 0,
        "Number of organizers": Organizer.objects.filter(organizers__in=reports).distinct().count() or 0,
        "Number of organizers retained": Organizer.objects.filter(retained=True, organizers__in=reports).distinct().count() or 0,
        # "Number of people reached through social media": reports.aggregate(total=Sum(F("number_of_people_reached_through_social_media")))["total"] or 0,
        "Occurence": reports.filter(metrics_related__boolean_type=True).exists() or False,
    }


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

