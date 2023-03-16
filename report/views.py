import datetime
import pandas as pd
import zipfile
from io import BytesIO

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib import messages

from metrics.models import Metric
from report.models import LearningArea, EvaluationObjective, EvaluationObjectiveAnswer, Editor, Organizer, Partner, \
    Funding, Technology, Report, AreaActivated
from users.models import TeamArea, UserProfile
from report.forms import NewReportForm, StrategicLearningQuestionsForm, activities_associated_as_choices,\
    AreaActivatedForm, FundingForm, PartnerForm, TechnologyForm


# CREATE
@login_required
def add_report(request):
    if request.method == "POST":
        form_valid_message = _("Report registered successfully!")
        form_invalid_message = _("Something went wrong!")

        report_form = NewReportForm(request.POST)

        if report_form.is_valid():
            report = report_form.save()

            user = get_object_or_404(UserProfile, user=request.user)
            editors = get_or_create_editors(request.POST["editors_string"])
            organizers = get_or_create_organizers(request.POST["organizers_string"])

            report.editors.set(editors)
            report.organizers.set(organizers)
            report.created_by = user
            report.modified_by = user

            report.save()

            strategic_learning_questions_form = StrategicLearningQuestionsForm(request.POST)
            if strategic_learning_questions_form.is_valid():
                strategic_learning_questions_form.save()
            else:
                pass
            messages.success(request, form_valid_message)
            return redirect(reverse("report:detail_report", kwargs={"report_id": report.id}))
        messages.error(request, form_invalid_message)
        context = {"report_form": report_form,
                   "directions_related_set": [],
                   "learning_questions_related_set": []}
        return render(request, "report/add_report.html", context)
    else:
        report_form = NewReportForm()
        strategic_learning_questions_form = StrategicLearningQuestionsForm()

    context = {"report_form": report_form,
               "strategic_learning_questions_form": strategic_learning_questions_form,
               "directions_related_set": [],
               "learning_questions_related_set": []}

    return render(request, "report/add_report.html", context)


def add_area_activated(request):
    if request.method == "POST":
        area_form = AreaActivatedForm(request.POST)
        if area_form.is_valid():
            if not AreaActivated.objects.filter(text=area_form.instance.text).count():
                area_form.save()
            return redirect(reverse("report:list_areas_activated"))
        context = {"area_form": area_form}
        return render(request, "area_activated/add_area.html", context)
    else:
        area_form = AreaActivatedForm()
        context = {"area_form": area_form}
        return render(request, "area_activated/add_area.html", context)


def list_areas(request):
    areas = AreaActivated.objects.all()

    context = {"dataset": areas}
    return render(request, "area_activated/list_areas.html", context)


def add_funding(request):
    if request.method == "POST":
        funding_form = FundingForm(request.POST)
        if funding_form.is_valid():
            if not Funding.objects.filter(name=funding_form.instance.name, value=funding_form.instance.value).count():
                funding_form.save()
            return redirect(reverse("report:list_fundings"))
        context = {"funding_form": funding_form}
        return render(request, "funding/add_funding.html", context)
    else:
        funding_form = FundingForm()
        context = {"funding_form": funding_form}
        return render(request, "funding/add_funding.html", context)


def list_fundings(request):
    fundings = Funding.objects.all()

    context = {"dataset": fundings}
    return render(request, "funding/list_fundings.html", context)


def add_partner(request):
    if request.method == "POST":
        partner_form = PartnerForm(request.POST)
        if partner_form.is_valid():
            if not Partner.objects.filter(name=partner_form.instance.name).count():
                partner_form.save()
            return redirect(reverse("report:list_partners"))
        context = {"partner_form": partner_form}
        return render(request, "partners/add_partner.html", context)
    else:
        partner_form = PartnerForm()
        context = {"partner_form": partner_form}
        return render(request, "partners/add_partner.html", context)


def list_partners(request):
    partners = Partner.objects.all()

    context = {"dataset": partners}
    return render(request, "partners/list_partners.html", context)


def add_technology(request):
    if request.method == "POST":
        technology_form = TechnologyForm(request.POST)
        if technology_form.is_valid():
            if not Technology.objects.filter(name=technology_form.instance.name).count():
                technology_form.save()
            return redirect(reverse("report:list_technologies"))
        context = {"technology_form": technology_form}
        return render(request, "technologies/add_technology.html", context)
    else:
        technology_form = TechnologyForm()
        context = {"technology_form": technology_form}
        return render(request, "technologies/add_technology.html", context)


def list_technologies(request):
    technologies = Technology.objects.all()

    context = {"dataset": technologies}
    return render(request, "technologies/list_technologies.html", context)

# REVIEW
@login_required
def list_reports(request):
    context = {"dataset": Report.objects.order_by('-modified_at'), "mine": False}

    return render(request, "report/list_reports.html", context)


@login_required
def detail_report(request, report_id):
    context = {"data": Report.objects.get(id=report_id),
               "evaluation_objective": EvaluationObjectiveAnswer.objects.filter(report_id=report_id)}

    return render(request, "report/detail_report.html", context)


def add_csv_file(function_name, report_id=None):
    csv_file = BytesIO()
    function_name(report_id).to_csv(path_or_buf=csv_file, index=False)

    return csv_file


def add_excel_file(report_id=None):
    excel_file = BytesIO()
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

    export_report_instance(report_id).to_excel(writer, sheet_name='Report', index=False)
    export_metrics(report_id).to_excel(writer, sheet_name='Metrics', index=False)
    export_user_profile(report_id).to_excel(writer, sheet_name='Users', index=False)
    export_area_activated(report_id).to_excel(writer, sheet_name='Areas', index=False)
    export_directions_related(report_id).to_excel(writer, sheet_name='Directions', index=False)
    export_editors(report_id).to_excel(writer, sheet_name='Editors', index=False)
    export_learning_questions_related(report_id).to_excel(writer, sheet_name='Learning questions', index=False)
    export_evaluation_objectives(report_id).to_excel(writer, sheet_name='Evaluation objectives', index=False)
    export_organizers(report_id).to_excel(writer, sheet_name='Organizers', index=False)
    export_partners_activated(report_id).to_excel(writer, sheet_name='Partners', index=False)
    export_technologies_used(report_id).to_excel(writer, sheet_name='Technologies', index=False)

    writer.save()
    return excel_file


@login_required
def export_report(request, report_id=None):
    buffer = BytesIO()
    zip_file = zipfile.ZipFile(buffer, mode="w")
    sub_directory = "csv/"

    if report_id:
        zip_name = _("Report")
        identifier = " {}".format(report_id)
    else:
        zip_name = _("SARA - Reports")
        identifier = ""

    posfix = identifier + " - {}".format(datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%S'))
    files = [[export_report_instance, sub_directory + 'Report' + posfix],
             [export_metrics, sub_directory + 'Metrics' + posfix],
             [export_user_profile, sub_directory + 'Users' + posfix],
             [export_area_activated, sub_directory + 'Areas' + posfix],
             [export_directions_related, sub_directory + 'Directions' + posfix],
             [export_editors, sub_directory + 'Editors' + posfix],
             [export_learning_questions_related, sub_directory + 'Learning questions' + posfix],
             [export_evaluation_objectives, sub_directory + 'Evaluation objectives' + posfix],
             [export_organizers, sub_directory + 'Organizers' + posfix],
             [export_partners_activated, sub_directory + 'Partners' + posfix],
             [export_technologies_used, sub_directory + 'Technologies' + posfix]]

    for file in files:
        zip_file.writestr('{}.csv'.format(file[1]), add_csv_file(file[0], report_id).getvalue())
    zip_file.writestr('Export' + posfix + '.xlsx', add_excel_file(report_id).getvalue())

    zip_file.close()

    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename=' + zip_name + posfix + '.zip'

    return response


def export_report_instance(report_id=None):
    header = [_('ID'), _('Created by'), _('Created at'), _('Modified by'), _('Modified at'), _('Activity associated'),
              _('Name of the activity'), _('Area responsible'), _('Area activated'), _('Initial date'), _('End date'),
              _('Description'), _('Funding associated'), _('Links'), _('Public communication'),
              _('Number of Participants'), _('Number of Resources'), _('Number of Feedbacks'), _('Editors'),
              _('Organizers'), _('Partnerships activated'), _('Technologies used'), _('# Wikipedia created'),
              _('# Wikipedia edited'), _('# Commons created'), _('# Commons edited'), _('# Wikidata created'),
              _('# Wikidata edited'), _('# Wikiversity created'), _('# Wikiversity edited'), _('# Wikibooks created'),
              _('# Wikibooks edited'), _('# Wikisource created'), _('# Wikisource edited'), _('# Wikinews created'),
              _('# Wikinews edited'), _('# Wikiquote created'), _('# Wikiquote edited'), _('# Wiktionary created'),
              _('# Wiktionary edited'), _('# Wikivoyage created'), _('# Wikivoyage edited'), _('# Wikispecies created'),
              _('# Wikispecies edited'), _('# Metawiki created'), _('# Metawiki edited'), _('# Mediawiki created'),
              _('# Mediawiki edited'), _('Directions related'), _('Learning'), _('Learning questions related')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        # Database
        id_ = report.id
        created_by = report.created_by
        created_at = report.created_at
        modified_by = report.modified_by
        modified_at = report.modified_at

        # Administrative
        activity_associated = report.activity_associated
        activity_other = report.activity_other or ""
        area_responsible = report.area_responsible
        area_activated = "; ".join(map(str, report.area_activated.values_list("id", flat=True)))
        initial_date = report.initial_date
        end_date = report.end_date
        description = report.description
        funding_associated = report.funding_associated
        links = report.links.replace("\r\n", "; ")
        public_communication = report.public_communication
        should_be_on_meta = report.should_be_on_meta

        # Quantitative
        participants = report.participants
        resources = report.resources
        feedbacks = report.feedbacks
        editors = "; ".join(report.editors.values_list("username", flat=True))
        organizers = "; ".join([x["name"] + " (" + x["institution__name"] + ")" for x in
                                report.organizers.values("name", "institution__name")])
        partners_activated = "; ".join(report.partners_activated.values_list("name", flat=True))
        technologies_used = "; ".join(report.technologies_used.values_list("name", flat=True))

        # Wikimedia
        wikipedia_created = report.wikipedia_created
        wikipedia_edited = report.wikipedia_edited
        commons_created = report.commons_created
        commons_edited = report.commons_edited
        wikidata_created = report.wikidata_created
        wikidata_edited = report.wikidata_edited
        wikiversity_created = report.wikiversity_created
        wikiversity_edited = report.wikiversity_edited
        wikibooks_created = report.wikibooks_created
        wikibooks_edited = report.wikibooks_edited
        wikisource_created = report.wikisource_created
        wikisource_edited = report.wikisource_edited
        wikinews_created = report.wikinews_created
        wikinews_edited = report.wikinews_edited
        wikiquote_created = report.wikiquote_created
        wikiquote_edited = report.wikiquote_edited
        wiktionary_created = report.wiktionary_created
        wiktionary_edited = report.wiktionary_edited
        wikivoyage_created = report.wikivoyage_created
        wikivoyage_edited = report.wikivoyage_edited
        wikispecies_created = report.wikispecies_created
        wikispecies_edited = report.wikispecies_edited
        metawiki_created = report.metawiki_created
        metawiki_edited = report.metawiki_edited
        mediawiki_created = report.mediawiki_created
        mediawiki_edited = report.mediawiki_edited

        # Strategy
        directions_related = "; ".join(map(str, report.directions_related.values_list("id", flat=True)))
        learning = report.learning.replace("\r\n", "\n")

        # Theory
        learning_questions_related = "; ".join(map(str, report.learning_questions_related.values_list("id", flat=True)))

        rows.append([id_, created_by, created_at, modified_by, modified_at, activity_associated, activity_other,
                     area_responsible, area_activated, initial_date, end_date, description, funding_associated, links,
                     public_communication, should_be_on_meta, participants, resources, feedbacks, editors,
                     organizers, partners_activated, technologies_used, wikipedia_created, wikipedia_edited,
                     commons_created, commons_edited, wikidata_created, wikidata_edited, wikiversity_created,
                     wikiversity_edited, wikibooks_created, wikibooks_edited, wikisource_created, wikisource_edited,
                     wikinews_created, wikinews_edited, wikiquote_created, wikiquote_edited, wiktionary_created,
                     wiktionary_edited, wikivoyage_created, wikivoyage_edited, wikispecies_created, wikispecies_edited,
                     metawiki_created, metawiki_edited, mediawiki_created, mediawiki_edited, directions_related,
                     learning, learning_questions_related])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()

    df[_('Created at')] = df[_('Created at')].dt.tz_localize(None)
    df[_('Modified at')] = df[_('Modified at')].dt.tz_localize(None)
    return df


def export_metrics(report_id=None):
    header = [_('ID'), _('Metric'), _('Activity ID'), _('Activity'), _('Activity code'), _('Number of editors'),
              _('Number of participants'), _('Number of partnerships'), _('Number of resources'),
              _('Number of feedbacks'), _('Number of events'), _('Other type? Which?'), _('Observation'),
              _('# Wikipedia created'), _('# Wikipedia edited'), _('# Commons created'), _('# Commons edited'),
              _('# Wikidata created'), _('# Wikidata edited'), _('# Wikiversity created'), _('# Wikiversity edited'),
              _('# Wikibooks created'), _('# Wikibooks edited'), _('# Wikisource created'), _('# Wikisource edited'),
              _('# Wikinews created'), _('# Wikinews edited'), _('# Wikiquote created'), _('# Wikiquote edited'),
              _('# Wiktionary created'), _('# Wiktionary edited'), _('# Wikivoyage created'), _('# Wikivoyage edited'),
              _('# Wikispecies created'), _('# Wikispecies edited'), _('# Metawiki created'), _('# Metawiki edited'),
              _('# Mediawiki created'), _('# Mediawiki edited')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.activity_associated.metrics.all():
            rows.append([instance.id, instance.text, instance.activity_id, instance.activity.text,
                         instance.activity.code, instance.number_of_editors, instance.number_of_participants,
                         instance.number_of_partnerships, instance.number_of_resources, instance.number_of_feedbacks,
                         instance.number_of_events, instance.other_type, instance.observation,
                         instance.wikipedia_created, instance.wikipedia_edited, instance.commons_created,
                         instance.commons_edited, instance.wikidata_created, instance.wikidata_edited,
                         instance.wikiversity_created, instance.wikiversity_edited, instance.wikibooks_created,
                         instance.wikibooks_edited, instance.wikisource_created, instance.wikisource_edited,
                         instance.wikinews_created, instance.wikinews_edited, instance.wikiquote_created,
                         instance.wikiquote_edited, instance.wiktionary_created, instance.wiktionary_edited,
                         instance.wikivoyage_created, instance.wikivoyage_edited, instance.wikispecies_created,
                         instance.wikispecies_edited, instance.metawiki_created, instance.metawiki_edited,
                         instance.mediawiki_created, instance.mediawiki_edited])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_user_profile(report_id=None):
    header = [_('ID'), _('Username on Wiki'), _('First name'), _('Last Name'),
              _('Email'), _('Lattes'), _('Orcid'), _('Google_scholar')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in [report.created_by, report.modified_by]:
            rows.append([instance.id, instance.professional_wiki_handle, instance.user.first_name, instance.user.last_name,
                         instance.user.email, instance.lattes, instance.orcid, instance.google_scholar])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_area_activated(report_id=None):
    header = [_('ID'), _('Area activated'), _('Contact')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.area_activated.all():
            rows.append([instance.id, instance.text, instance.contact])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_directions_related(report_id=None):
    header = [_('ID'), _('Direction related'), _('Strategic axis ID'), _('Strategic axis text')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.directions_related.all():
            rows.append([instance.id, instance.text, instance.strategic_axis_id, instance.strategic_axis.text])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_editors(report_id=None):
    header = [_('ID'), _('Username')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.editors.all():
            rows.append([instance.id, instance.username])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_learning_questions_related(report_id=None):
    header = [_('ID'), _('Learning question'), _('Learning area ID'), _('Learning area')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.learning_questions_related.all():
            rows.append([instance.id, instance.text, instance.learning_area_id, instance.learning_area.text])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_evaluation_objectives(report_id=None):
    header = [_('ID'), _('Evaluation objectives'), _('Evaluation answers'), _('Learning area ID'), _('Learning area')]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        objectives = EvaluationObjective.objects.filter(
            learning_area_of_objective__strategic_question__in=report.learning_questions_related.all())
        for instance in objectives.all():
            answer = EvaluationObjectiveAnswer.objects.get(objective=instance, report=report)
            rows.append([instance.id,
                         instance.text,
                         answer.answer,
                         instance.learning_area_of_objective_id,
                         instance.learning_area_of_objective.text])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_organizers(report_id=None):
    header = [_('ID'), _("Organizer's name"), _("Organizer's institution ID"), _("Organizer institution's name")]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.organizers.all():
            rows.append([instance.id, instance.name, instance.institution.name])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_partners_activated(report_id=None):
    header = [_('ID'), _("Partners"), _("Partner's website")]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.partners_activated.all():
            rows.append([instance.id, instance.name, instance.website])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


def export_technologies_used(report_id=None):
    header = [_('ID'), _("Technology")]

    if report_id:
        reports = Report.objects.filter(pk=report_id)
    else:
        reports = Report.objects.all()

    rows = []
    for report in reports:
        for instance in report.technologies_used.all():
            rows.append([instance.id, instance.name])

    df = pd.DataFrame(rows, columns=header).drop_duplicates()
    return df


# UPDATE
@login_required
def update_report(request, report_id):
    obj = get_object_or_404(Report, id=report_id)
    report_form = NewReportForm(request.POST or None, instance=obj)

    if request.method == "POST":
        if report_form.is_valid():
            report_instance = report_form.save(commit=False)
            user_profile = UserProfile.objects.get(user=request.user)
            editors = get_or_create_editors(request.POST["editors_string"])
            organizers = get_or_create_organizers(request.POST["organizers_string"])

            report_instance.editors.set(editors)
            report_instance.organizers.set(organizers)
            report_instance.modified_by = user_profile
            report_instance.modified_at = datetime.datetime.now()

            report_instance.save()
            update_answers(report_instance.learning_questions_related.all(), report_id)
            save_answers(request.POST, report_id)
            return redirect(reverse("report:detail_report", kwargs={"report_id": report_id}))

    context = {"report_form": report_form,
               "directions_related_set": list(obj.directions_related.values_list("id", flat=True)),
               "learning_questions_related_set": list(obj.learning_questions_related.values_list("id", flat=True))}

    return render(request, "report/add_report.html", context)


def update_answers(learning_areas, report_id):
    filtered_answers = EvaluationObjectiveAnswer.objects.filter(report_id=report_id)
    excluded_answers = filtered_answers.exclude(
        objective__learning_area_of_objective_id__in=list(learning_areas.values_list("id", flat=True)))
    excluded_answers.delete()


def save_answers(form, report_id):
    objectives = EvaluationObjective.objects.values_list("id", flat=True)
    for objective_id in objectives:
        if "objective_answer_" + str(objective_id) in form:
            answer, answer_created = EvaluationObjectiveAnswer.objects.get_or_create(objective_id=objective_id,
                                                                                     report_id=report_id)
            answer.answer = form["objective_answer_" + str(objective_id)]
            answer.save()


# DELETE
@login_required
def delete_report(request, report_id):
    report = Report.objects.get(id=report_id)
    context = {"report": report}

    if request.method == "POST":
        report.delete()
        return redirect(reverse('report:list_reports'))

    return render(request, 'report/delete_report.html', context)


# FUNCTIONS
def get_or_create_editors(editors_string):
    editors_list = editors_string.split("\r\n")
    editors = []
    if editors_string:
        for editor in editors_list:
            new_editor, created = Editor.objects.get_or_create(username=editor)
            editors.append(new_editor)

    return editors


def get_or_create_organizers(organizers_string):
    organizers_list = organizers_string.split("\r\n")
    organizers = []
    if organizers_string:
        for organizer in organizers_list:
            organizer_name, institution_name = (organizer + ";").split(";", maxsplit=1)
            new_organizer, new_organizer_created = Organizer.objects.get_or_create(name=organizer)
            if institution_name:
                for partner_name in institution_name.split(";"):
                    partner, partner_created = Partner.objects.get_or_create(name=partner_name)
                    if partner_created:
                        new_organizer.institution.add(partner)
                new_organizer.save()
            organizers.append(new_organizer)
    return organizers


@login_required
def get_activities(request):
    activities = activities_associated_as_choices()
    return JsonResponse({'activities': list(activities)})


@login_required
def get_areas(request):
    areas = AreaActivated.objects.all()
    return JsonResponse({'areas': list(areas.values())})


@login_required
def get_fundings(request):
    fundings = Funding.objects.all()
    return JsonResponse({'fundings': list(fundings.values())})


@login_required
def get_partnerships(request):
    partnerships = Partner.objects.all()
    return JsonResponse({'partnerships': list(partnerships.values())})


@login_required
def get_technologies(request):
    technologies = Technology.objects.all()
    return JsonResponse({'technologies': list(technologies.values())})


@login_required
def get_metrics(request):
    activity_id = int(request.GET["id"])
    metrics = Metric.objects.filter(activity_id=activity_id)
    return JsonResponse({'metrics': list(metrics.values())})


@login_required
def get_objectives(request):
    strategic_learning_question_id = int(request.GET["question_id"])
    report_id_aux = request.GET["report_id"]
    report_id = int(report_id_aux) if report_id_aux != "None" else 0
    learning_area = LearningArea.objects.get(strategic_question=strategic_learning_question_id)
    if report_id and EvaluationObjectiveAnswer.objects.filter(objective__learning_area_of_objective=learning_area,
                                                              report_id=report_id).count():
        answers = EvaluationObjectiveAnswer.objects.filter(objective__learning_area_of_objective=learning_area,
                                                           report_id=report_id)
        return JsonResponse({'answers': list(answers.values_list("id", "answer", "objective__id", "objective__text"))})
    else:
        objectives = EvaluationObjective.objects.filter(learning_area_of_objective=learning_area)
        answers = []
        for objective in objectives:
            answers.append([None, None, objective.id, objective.text])

        return JsonResponse({'answers': answers})
