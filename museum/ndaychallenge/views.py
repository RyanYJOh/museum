from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import User
from .models import Challenge
from main.models import AnswersForFromUs
from member.models import UserInfo
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import date, datetime
import json
import random
from django.core.paginator import Paginator
from django.db.models import Count

# Create your views here.

##### 공통 영역 #####
now = timezone.now()
string__today = str(timezone.now()).split()[0]
today = datetime.strptime(string__today, '%Y-%m-%d').date()

def navbar(request):
    # navbar_this_user = User.objects.get(user=request.user)
    if request.user.is_authenticated:
        navbar_this_user = request.user
        try:
            navbar_this_userinfo = UserInfo.objects.get(this_user=navbar_this_user)
            navbar_authenticated = 'True'

            navbar_context = {
                'navbar_authenticated' : navbar_authenticated,
                'navbar_this_user' : navbar_this_user.username,
                'navbar_this_userinfo' : navbar_this_userinfo,
            }
        except ObjectDoesNotExist:
            navbar_authenticated = 'False'
            navbar_context = {
                navbar_authenticated : navbar_authenticated,
                'navbar_this_user' : navbar_this_user.username,
            }
    else:
        navbar_authenticated = 'False'

        navbar_context = {
            'navbar_authenticated' : navbar_authenticated,
        }
    
    return navbar_context

def ndaychallenge(request, id):
    navbar_context = navbar(request)
    ## 이번 Challenge
    this_challenge = Challenge.objects.get(id=id)

    # 날짜가 지났는가
    if today < this_challenge.start_date:
        available = 'before'
    elif today >= this_challenge.start_date and today <= this_challenge.end_date:
        available = 'current'
    elif today > this_challenge.end_date:
        available = 'after'
    
    ## 각 유저의 남은 답변 갯수
    participants = this_challenge.participant.values_list('this_user', flat=True).order_by('?')
    list__participants = list(participants)
    total_participants = participants.count()

    answers_since_start_date = AnswersForFromUs.objects.filter(author_id__in=list__participants, created_at__gte=this_challenge.start_date)
    
    ## 모든 답변 가져오기
    answers_is_shared_true = answers_since_start_date.filter(is_shared=True)
    paginator_is_shared_true = Paginator(answers_is_shared_true, 10)
    page_is_shared_true = request.GET.get('page')
    is_shared_paginated = paginator_is_shared_true.get_page(page_is_shared_true)
    
    list__challenge_data = []
    for p in participants:
        dict__challenge_data = {}
        this_user_ans = answers_since_start_date.filter(author_id=p).count()
        this_user_info = UserInfo.objects.get(this_user=p)
        
        dict__challenge_data['author'] = this_user_info.real_name
        dict__challenge_data['profile_image'] = this_user_info.profile_image
        dict__challenge_data['count'] = this_user_ans
        if this_user_ans >= this_challenge.pass_condition:
            dict__challenge_data['progress'] = 100
        else:
            dict__challenge_data['progress'] = (this_user_ans/this_challenge.pass_condition)*100
        list__challenge_data.append(dict__challenge_data)
    
    
    remaining = str(this_challenge.end_date - today).split('days')[0]
    pre_context = {
        'available' : available,
        'this_challenge' : this_challenge,
        'participants' : participants,
        'answers_since_start_date' : answers_since_start_date,
        'list__challenge_data' : list__challenge_data,
        'pass_condition' : this_challenge.pass_condition,
        'today' : today,
        'end_date' : this_challenge.end_date,
        'remaining' : remaining,
        'is_shared_paginated' : is_shared_paginated,
        'total_participants' : total_participants,
    }

    context = {**navbar_context, **pre_context}
    return render(request, 'ndaychallenge/nday.html', context)