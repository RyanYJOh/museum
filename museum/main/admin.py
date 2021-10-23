from django.contrib import admin
from .models import QuestionsFromUs, QuestionsFromSelf, AnswersForFromSelf, AnswersForFromUs, RandomImages, SavedAnswers, CommentAnsUs
# Register your models here.

class MainAdmin(admin.ModelAdmin):
    readonly_fields = ('id'),

admin.site.register(QuestionsFromSelf, MainAdmin)
admin.site.register(QuestionsFromUs, MainAdmin)
admin.site.register(AnswersForFromUs, MainAdmin)
admin.site.register(AnswersForFromSelf, MainAdmin)
admin.site.register(SavedAnswers, MainAdmin)
admin.site.register(RandomImages, MainAdmin)
admin.site.register(CommentAnsUs, MainAdmin)