from django.contrib import admin
from .models import EvaluationObjective, Report, AreaActivated, Editor, Funding, LearningArea, Organizer, Partner, \
    Technology, StrategicLearningQuestion, OperationReport

admin.site.register(Funding)
admin.site.register(Editor)
admin.site.register(Partner)
admin.site.register(Organizer)
admin.site.register(Technology)
admin.site.register(AreaActivated)
admin.site.register(LearningArea)
admin.site.register(StrategicLearningQuestion)
admin.site.register(EvaluationObjective)
admin.site.register(Report)
admin.site.register(OperationReport)
