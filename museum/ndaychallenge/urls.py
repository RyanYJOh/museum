from django.urls import path
from . import views

urlpatterns = [
    # path('', views.ndaychallenge, name='challenge-home'),
    path('n-day/<int:id>', views.ndaychallenge, name="nday-challenge")
    
] 