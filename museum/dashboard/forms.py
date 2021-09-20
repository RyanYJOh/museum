from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Clicks

class ClicksForm(forms.ModelForm):
    clicked_from = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Clicks
        fields = ('clicked_from', )