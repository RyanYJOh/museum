from django.contrib import admin
from .models import UserInfo, UserInfoAdditional
# Register your models here.

admin.site.register(UserInfo)
admin.site.register(UserInfoAdditional)
