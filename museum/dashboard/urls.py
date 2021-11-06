from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('kpi', views.kpi, name='kpi'),
    path('download/ans-us', views.xlsx_ans_us, name='xlsx_ans_us'),
    path('download/ans-self', views.xlsx_ans_self, name='xlsx_ans_self'),

]