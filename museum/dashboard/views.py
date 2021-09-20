from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from datetime import date, datetime
from main.models import AnswersForFromSelf, AnswersForFromUs
from member.models import UserInfo
from .forms import ClicksForm
import json

# Create your views here.
def clicks(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)

        clicked_from = data['clicked_from']
        ans_type = data['ans_type']
        ans_us_ref = data['ans_us_ref']
        ans_self_ref = data['ans_self_ref']
        
        ## whose_post
        if ans_type == 'us':
            this_ans = AnswersForFromUs.objects.get(id=ans_us_ref)
            author_id = getattr(this_ans, 'author_id')
            print('author id is ', author_id)
            whose_post = User.objects.get(username=author_id)
        elif ans_type == 'self':
            this_ans = AnswersForFromSelf.objects.get(id=ans_self_ref)
            author_id = getattr(this_ans, 'author_id')
            print('author id is ', author_id)
            whose_post = User.objects.get(username=author_id)
        
        clicked_by = request.user
        get_this_user = UserInfo.objects.get(this_user=request.user)
        clicked_user_type = getattr(get_this_user, 'persona_type')
        print(clicked_user_type)

        if request.method == 'POST':
            form = ClicksForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                
                instance.clicked_from = clicked_from
                instance.whose_post = whose_post
                instance.ans_type = ans_type
                if ans_type == 'us':
                    instance.ans_us_ref = AnswersForFromUs.objects.get(id=ans_us_ref) 
                elif ans_type == 'self':
                    instance.ans_self_ref = AnswersForFromSelf.objects.get(id=ans_self_ref) 
                instance.clicked_by = clicked_by
                instance.clicked_user_type = clicked_user_type
        
                instance.save()
                print('successful!!!!!!!!!!!!!!!')
                
                ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                return redirect('/me')
            else:
                print('@@@@@@ Validation failed due to : ', form.errors)
                
    else:
        pass