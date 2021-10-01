from django.urls import path
from . import views

urlpatterns = [
    # path('', views.main_page, name='home'),
    path('', views.dashboard, name='dashboard'),

]