from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import UserInfo

class UserInfoForm(forms.ModelForm):
    PERSONA_TYPE = (
        ('Adam', '배울점이 있는 사람들의 생각을 접하며 삶에 동기부여를 받아요.'),
        ('Brian','나에게 생각할거리가 주어지는 것을 좋아해요.'),
        ('Claire','나의 생각을 글이나 메모로 정리하는 데 익숙해요.'),
        # ('Diana','삶에 동기부여를 주는 컨텐츠를 자주 찾아봐요.'),
        ('Other','(기타) 어느 것에도 크게 해당되지 않아요.')
    )

    real_name = forms.CharField(label = "이름", max_length=20, required=True,
    widget=forms.TextInput(attrs={
    }))

    profile_image = forms.ImageField(label="", required=False)

    self_intro = forms.CharField(max_length=140, required=False, 
    widget=forms.Textarea(attrs={
        'rows' : 3
    }))

    persona_type = forms.ChoiceField(required=True, choices=PERSONA_TYPE, 
    widget=forms.RadioSelect
    )

    class Meta:
        model = UserInfo
        fields = ('real_name', 'profile_image', 'self_intro', 'persona_type')