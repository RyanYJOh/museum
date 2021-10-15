from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.
class MyUserAdmin(UserAdmin):
    ordering = ('-date_joined',)
    list_display = ('username', 'date_joined', 'is_superuser')

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)