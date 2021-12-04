from django.contrib import admin
from .models import QuestionsFromOthers, AnswersForFromOthers
# Register your models here.

class QuestionsquareAdmin(admin.ModelAdmin):
    readonly_fields = ('id'),

admin.site.register(QuestionsFromOthers, QuestionsquareAdmin)
admin.site.register(AnswersForFromOthers, QuestionsquareAdmin)