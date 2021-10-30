from django.contrib import admin
from main.models import AnswersForFromUs
from .models import Challenge

# Register your models here.
class NdaychallengeAdmin(admin.ModelAdmin):
    readonly_fields = ('id'),

admin.site.register(Challenge, NdaychallengeAdmin)