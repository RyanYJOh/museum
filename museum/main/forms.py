from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import QuestionsFromSelf, AnswersForFromUs, AnswersForFromSelf, SavedAnswers, CommentAnsUs, CommentAnsSelf

class QuestionsFromSelfForm(forms.ModelForm):
    title = forms.CharField(label="", required=False, widget=forms.TextInput( ## Validation은 클라에서 진행
        attrs={
            'placeholder' : '내가 나에게 던지는 질문',
            # 'style':'font-size:3rem;'
        }))
    image = forms.ImageField(label="", required=False)

    class Meta:
        model = QuestionsFromSelf
        fields = ('title', 'image')

class AnswersForFromUsForm(forms.ModelForm):
    body = forms.CharField(label = "", required=False, widget=forms.Textarea(
        attrs={
            'class' : 'form-control',
            'placeholder' : '나의 답변이 곧 나의 정답',
            'rows' : 7,
        }
    ))
    image = forms.ImageField(label="", required=False)
    is_shared = forms.BooleanField(required=False)

    class Meta:
        model = AnswersForFromUs
        fields = ('body', 'image', 'is_shared')

class AnswersForFromSelfForm(forms.ModelForm):

    subtitle = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={
            'placeholder' : '부제: 무엇에 대한 글인가',
            'style':'font-size:1.063rem;'
        }
    ))
    body = forms.CharField(label="", required=False, widget=forms.Textarea(
        attrs={
            'placeholder' : '나의 생각이 곧 나의 정답',
            'style':'font-size:1.063rem;',
            'rows' : 30
        }
    ))
    # image = forms.ImageField(required=False)
    is_shared =forms.BooleanField(label="", required=False)
    
    class Meta:
        model = AnswersForFromSelf
        fields = ('subtitle', 'body', 'is_shared')

class SavedAnswersForm(forms.ModelForm):
    ans_no = forms.IntegerField(required=False)
    ans_type = forms.CharField(required=False)
    bookmarker = forms.CharField(required=False)

    class Meta:
        model = SavedAnswers
        fields = ('ans_no', 'ans_type', 'bookmarker')

class CommentAnsUsForm(forms.ModelForm):
    body = forms.CharField(label="", required=False, widget=forms.Textarea(
        attrs={
            'placeholder' : '멋진 사람과의 교류는 늘 설레는 일',
            'rows' : 2,
        }
    ))
    class Meta:
        model = CommentAnsUs
        fields = ('body',)

class CommentAnsSelfForm(forms.ModelForm):
    body = forms.CharField(label="", required=False, widget=forms.Textarea(
        attrs={
            'placeholder' : '멋진 사람과의 교류는 늘 설레는 일',
            'rows' : 2,
        }
    ))
    class Meta:
        model = CommentAnsSelf
        fields = ('body',)

class SearchForm(forms.Form):
    WHICH = (
        ('answer', '답변'),
        ('question','질문'),
        ('user','유저'),
    )

    search_keyword = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs = {
            'placeholder' : '찾고야 말 테다',
            'class' : 'search-form'
        }
    ))
    which = forms.ChoiceField(label="", required=False, choices=WHICH, 
        widget=forms.Select(
            attrs= {
                # 'class' : 'dropdown'
            }
        )
    )
    class Meta: 
        fields = ('search_keyword', 'which')