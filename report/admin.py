from django.contrib import admin
from .models import EvaluationObjective, Report, EvaluationObjectiveAnswer, AreaActivated, Editor, Funding, \
    LearningArea, Organizer, Partner, Technology, StrategicLearningQuestion

admin.site.register(EvaluationObjective)
admin.site.register(Report)
admin.site.register(EvaluationObjectiveAnswer)
admin.site.register(Editor)
admin.site.register(Funding)
admin.site.register(LearningArea)
admin.site.register(Organizer)
admin.site.register(Partner)
admin.site.register(Technology)
admin.site.register(StrategicLearningQuestion)
admin.site.register(AreaActivated)
