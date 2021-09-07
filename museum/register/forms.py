from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.forms import fields

## (UserCreationForm)의 모든 property를 가져오겠다.
class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        
        }))
    email = forms.EmailField(widget=forms.TextInput(attrs={

    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={

    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        
    }))

    class Meta: ## 이 RegisterForm에 있는 내용을 User DB에 저장하겠다는 Class
        model = User
        fields = ['username', 'email', 'password1', 'password2']
