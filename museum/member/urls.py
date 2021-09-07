from django.urls import path
from . import views

urlpatterns = [
    path('userinfo', views.create_userinfo, name='create_userinfo'),
    path('edit-userinfo/<str:username>', views.update_userinfo, name='update-userinfo'),
    # path('dansangmain', views.dansangMain, name='dansangmain'),
    # path('dansangdetail/<int:authuser_id>/<str:slug>', views.dansangDetail, name='dansangdetail'),
    # path('delete/<int:authuser_id>/<str:slug>', views.dansangDelete, name='dansangDelete'),
    # path('update/<int:authuser_id>/<str:slug>', views.dansangUpdate, name='dansangUpdate'),
]