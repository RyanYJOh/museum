from django.contrib import admin
from .models import Clicks
# Register your models here.

# class Dashboard(admin.ModelAdmin):
#     readonly_fields = ('id'),

admin.site.register(Clicks)