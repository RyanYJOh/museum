from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import QuestionsFromOthers, AnswersForFromOthers

class QuestionsFromOthersForm(forms.ModelForm):
    title = forms.CharField(label="", required=False, widget=forms.TextInput( ## Validation은 클라에서 진행. main.forms 참고
        attrs={
            'placeholder' : '어떤 질문을 던질까요?'
        }
    ))
    desc = forms.CharField(label="", required=False, widget=forms.Textarea(
        attrs={
            'class' : 'form-control',
            'placeholder' : '질문에 대해 조금 더 설명해주세요.',
            'rows' : 5,
        }
    ))
    image = forms.ImageField(label="", required=False)

    class Meta:
        model=QuestionsFromOthers
        fields = ('title', 'desc', 'image')

class AnswersForFromOthersForm(forms.ModelForm):
    body = forms.CharField(label="", required=False, widget=forms.Textarea(
        attrs={
            'class' : 'form-control',
            'placeholder' : '나의 답변이 곧 나의 정답',
            'rows' : 7,
        }
    ))
    image = forms.ImageField(label="", required=False)

    class Meta:
        model = AnswersForFromOthers
        fields = ('body', 'image')