from django.contrib.auth.models import User
from django.db.models.aggregates import Avg
from django.shortcuts import render, redirect, HttpResponse
from datetime import date, datetime
from main.models import AnswersForFromSelf, AnswersForFromUs, SavedAnswers, QuestionsFromUs
from .models import Clicks
from .forms import ClicksForm
from member.models import UserInfo
from django.contrib.auth.decorators import login_required
import json
from collections import defaultdict
import itertools
import numpy

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

            whose_post = User.objects.get(username=author_id)
        elif ans_type == 'self':
            this_ans = AnswersForFromSelf.objects.get(id=ans_self_ref)
            author_id = getattr(this_ans, 'author_id')

            whose_post = User.objects.get(username=author_id)
        
        clicked_by = request.user
        get_this_user = UserInfo.objects.get(this_user=request.user)
        clicked_user_type = getattr(get_this_user, 'persona_type')

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

def personaStaff():
    personaStaff = UserInfo.objects.filter(persona_type = 'Staff').values('this_user')
    list__staffId = []
    for i in range(0, len(personaStaff)):
        list__staffId.append(list(personaStaff)[i]['this_user'])
    
    return list__staffId

def dashboard(request):
    personaStaff = UserInfo.objects.filter(persona_type = 'Staff').values('this_user')
    list__staffId = []
    for i in range(0, len(personaStaff)):
        list__staffId.append(list(personaStaff)[i]['this_user'])

    today = date.today
    
    if request.user.is_superuser:
        message = "Originals Dashboard!"

        ## Persona type별 유저 수
        countAdam = UserInfo.objects.filter(persona_type='Adam').count()
        countBrian = UserInfo.objects.filter(persona_type='Brian').count()
        countClaire = UserInfo.objects.filter(persona_type='Claire').count()
        countOther = UserInfo.objects.filter(persona_type='Other').count()

        totalCountUsers = countAdam + countBrian + countClaire + countOther

        ## Persona type별 [나에게 던지는 질문] 갯수
        allSelfs = AnswersForFromSelf.objects.all().values('author_id') # [{'author_id': 아이디}, ...]
        list__allSelfs = []
        for i in range(0, len(allSelfs)):
            userId = allSelfs[i]['author_id']
        
            queryset__userType = UserInfo.objects.filter(this_user=userId).values('persona_type') # Queryset
            userType = queryset__userType[0]['persona_type']
            list__allSelfs.append(userType)

        countSelfByAdam = list__allSelfs.count('Adam')
        countSelfByBrian = list__allSelfs.count('Brian')
        countSelfByClaire = list__allSelfs.count('Claire')
        countSelfByOther = list__allSelfs.count('Other')
        totalCountSelfs = countSelfByAdam + countSelfByBrian + countSelfByClaire + countSelfByOther

        ## Persona type별 [오리지널스가 던지는 질문] 갯수
        allUss = AnswersForFromUs.objects.all().values('author_id') # [{'author_id': 아이디}, ...]
        list__allUss = []
        for i in range(0, len(allUss)):
            userId = allUss[i]['author_id']
        
            queryset__userType = UserInfo.objects.filter(this_user=userId).values('persona_type') # Queryset
            userType = queryset__userType[0]['persona_type']
            list__allUss.append(userType)

        countUsByAdam = list__allUss.count('Adam')
        countUsByBrian = list__allUss.count('Brian')
        countUsByClaire = list__allUss.count('Claire')
        countUsByOther = list__allUss.count('Other')
        totalCountUss = countUsByAdam + countUsByBrian + countUsByClaire + countUsByOther

        ## Persona Type별 북마크 수
        allBookmarkers = SavedAnswers.objects.all().values('bookmarker') # [{'bookmarker': 유저 아이디}, ...]
        
        list__userTypes = []
        for i in range(0, len(allBookmarkers)):
            userId = allBookmarkers[i]['bookmarker']
        
            queryset__userType = UserInfo.objects.filter(this_user=userId).values('persona_type') # Queryset
            userType = queryset__userType[0]['persona_type']
            list__userTypes.append(userType)

        countBookmarkByAdam = list__userTypes.count('Adam')
        countBookmarkByBrian = list__userTypes.count('Brian')
        countBookmarkByClaire = list__userTypes.count('Claire')
        countBookmarkByOther = list__userTypes.count('Other')
        totalBookmarks = countBookmarkByAdam + countBookmarkByBrian + countBookmarkByClaire + countBookmarkByOther

        ## 공개 Vs 미공개 컨텐츠 수
        
        allSelfsSharedFalse = AnswersForFromSelf.objects.filter(is_shared=False).exclude(author_id__in=list__staffId).count()
        allSelfsSharedTrue = AnswersForFromSelf.objects.filter(is_shared=True).exclude(author_id__in=list__staffId).count()
        allUssSharedFalse = AnswersForFromUs.objects.filter(is_shared=False).exclude(author_id__in=list__staffId).count()
        allUssSharedTrue = AnswersForFromUs.objects.filter(is_shared=True).exclude(author_id__in=list__staffId).count()

        sharedFalse = allSelfsSharedFalse + allUssSharedFalse
        sharedTrue = allSelfsSharedTrue + allUssSharedTrue
        totalAnswers = sharedFalse + sharedTrue

        ## Persona type별 클릭수 <- 여기서만 persona Other 제외 하..
        personaOther = UserInfo.objects.filter(persona_type = 'Staff').values('this_user')
        list__OtherId = []
        for i in range(0, len(personaOther)):
            list__OtherId.append(list(personaStaff)[i]['this_user'])
        totalClicks = Clicks.objects.all().exclude(clicked_by__in=list__OtherId).count()

        ## Persona type별 QuestionsFromUs 답변 주기 (= AnswersForFromUs 생성 주기)
        ## 각 유저 담아오기 : [{username : persona_type} , ...]의 구조로
        eachUser = User.objects.all().values_list('id', flat=True)
        list__eachUser = list(eachUser)

        dict__persona_type = {}
        dict__created_at = {}
        # for u in range(0, len(list__eachUser)):
        for u in list__eachUser:
            # this_userinfo = UserInfo.objects.get(this_user=list__eachUser[u])
            this_userinfo = UserInfo.objects.get(this_user = u)
            dict__persona_type[this_userinfo.real_name] = this_userinfo.persona_type # {real_name : persona_type}
            ## 각 유저의 AnswersForFromUs의 created_at 가져오기
            # 각 유저의 created_ats 리스트
            ans_from_us_created_ats = AnswersForFromUs.objects.filter(author_id=u).order_by('created_at').values_list('created_at', flat=True)
            list__ans_from_us_created_ats = list(ans_from_us_created_ats)
            # created_ats 차이로 이루어진 리스트
            list__created_ats_gap = []
            for c in range(0, len(list__ans_from_us_created_ats)):
                if c+1 < len(list__ans_from_us_created_ats):
                    gap = list__ans_from_us_created_ats[c+1]-list__ans_from_us_created_ats[c]
                    list__created_ats_gap.append(gap.days)
    
                    dict__created_at[this_userinfo.real_name] = list__created_ats_gap # {'real_name' : [created_at 차이]}
                else:
                    pass
        # persona_type별로 group_by
        users_by_persona = defaultdict(list)
        created_at_gaps_by_persona = defaultdict(list)
        for key, val in sorted(dict__persona_type.items()):
            users_by_persona[val].append(key)
            try:
                created_at_gaps_by_persona[val].append(dict__created_at[key])
            except KeyError:
                pass
        
        # 페르소나별 created_at의 차이
        dict__created_at_gaps_by_persona = dict(created_at_gaps_by_persona)
        dict__created_at_stats = {}
        for key, val in dict__created_at_gaps_by_persona.items():
            list__created_at_stats = []
            dict__created_at_gaps_by_persona[key] = list(itertools.chain.from_iterable(val))

            if len(dict__created_at_gaps_by_persona[key]) == 0:
                min_gap = '-'
                max_gap = '-'
                avg_gap = '-'
                median_gap = '-'
            else:
                min_gap = numpy.min(dict__created_at_gaps_by_persona[key])
                max_gap = numpy.max(dict__created_at_gaps_by_persona[key])
                avg_gap = round(numpy.mean(dict__created_at_gaps_by_persona[key]), 2)
                median_gap = numpy.median(dict__created_at_gaps_by_persona[key])

            list__created_at_stats.append(min_gap)
            list__created_at_stats.append(max_gap)
            list__created_at_stats.append(avg_gap)
            list__created_at_stats.append(median_gap)
            dict__created_at_stats[key] = list__created_at_stats
        
        context = {
            'message' : message,
            'date' : today,
            'current_user' : request.user,

            'countAdam' : countAdam,
            'countBrian' : countBrian,
            'countClaire' : countClaire,
            'countOther' : countOther,
            'totalCountUsers' : totalCountUsers,

            'countSelfByAdam' : countSelfByAdam,
            'countSelfByBrian' : countSelfByBrian,
            'countSelfByClaire' : countSelfByClaire,
            'countSelfByOther' : countSelfByOther,
            'totalCountSelfs' : totalCountSelfs,

            'countUsByAdam' : countUsByAdam,
            'countUsByBrian' : countUsByBrian,
            'countUsByClaire' : countUsByClaire,
            'countUsByOther' : countUsByOther,
            'totalCountUss' : totalCountUss,

            'countBookmarkByAdam' : countBookmarkByAdam,
            'countBookmarkByBrian' : countBookmarkByBrian,
            'countBookmarkByClaire' : countBookmarkByClaire,
            'countBookmarkByOther' : countBookmarkByOther,
            'totalBookmarks' : totalBookmarks,

            'sharedFalse' : sharedFalse,
            'sharedTrue' : sharedTrue,
            'totalAnswers' : totalAnswers,

            'totalClicks' : totalClicks,

            'users_by_persona' : users_by_persona,
            'dict__created_at_stats' : dict__created_at_stats,
            'dict__created_at_gaps_by_persona': dict__created_at_gaps_by_persona,
        }
    else:
        message = "관계자 외 출입 금지"
        context = {
            'message' : message,
            'current_user' : request.user,
        }
    return render(request, 'dashboard/home.html', context)

def kpi(request):
    ## 기본 셋팅
    today = date.today
    personaStaff = UserInfo.objects.filter(persona_type = 'Staff').values('this_user')
    list__staffId = []
    for i in range(0, len(personaStaff)):
        list__staffId.append(list(personaStaff)[i]['this_user'])
    
    ## Main body
    if request.user.is_superuser:
        message = "KPI를 달성해보자"

        ## 1. Retention by Persona, as well as total

        ## 2. 몇번 질문까지 쓰고 이탈하나

    else:
        message = "YOU HAVE NO ACCESS."
    
    context = {
        'message' : message,
        'today' : today,
    }
    return render(request, 'dashboard/kpi.html', context)


import xlwt

def xlsx_ans_us(request):
	
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment;filename*=UTF-8\'\'ans-us.xls' 
    wb = xlwt.Workbook(encoding='ansi') #encoding은 ansi로 해준다.
    ws = wb.add_sheet('오리지널스가 던지는 질문') #시트 추가
    
    row_num = 0
    col_names = ['question_id', 'author_id', 'created_at']
    
    #열이름을 첫번째 행에 추가 시켜준다.
    for idx, col_name in enumerate(col_names):
    	ws.write(row_num, idx, col_name)
        
    
    #데이터 베이스에서 유저 정보를 불러온다.
    rows = AnswersForFromUs.objects.all().values_list('question_id', 'author_id', 'created_at').order_by('-created_at_time')
    
    #유저정보를 한줄씩 작성한다.
    for row in rows:
        row_num += 1
        for col_num, attr in enumerate(row):

            ## 날짜 타입 변경
            if isinstance(attr, date):
                print('before : ', attr)
                attr = attr.strftime('%Y-%m-%d')
                print('after : ', attr)
            else: 
                pass
            ws.write(row_num, col_num, attr)
            
    wb.save(response)
    
    return response

def xlsx_ans_self(request):
	
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment;filename*=UTF-8\'\'ans-self.xls' 
    wb = xlwt.Workbook(encoding='ansi') #encoding은 ansi로 해준다.
    ws = wb.add_sheet('나에게 던지는 질문') #시트 추가
    
    row_num = 0
    col_names = ['question_id', 'author_id', 'created_at']
    
    #열이름을 첫번째 행에 추가 시켜준다.
    for idx, col_name in enumerate(col_names):
    	ws.write(row_num, idx, col_name)
        
    
    #데이터 베이스에서 유저 정보를 불러온다.
    rows = AnswersForFromSelf.objects.all().values_list('question_id', 'author_id', 'created_at').order_by('-created_at_time')
    
    #유저정보를 한줄씩 작성한다.
    for row in rows:
        row_num += 1
        for col_num, attr in enumerate(row):

            ## 날짜 타입 변경
            if isinstance(attr, date):
                print('before : ', attr)
                attr = attr.strftime('%Y-%m-%d')
                print('after : ', attr)
            else: 
                pass
            ws.write(row_num, col_num, attr)
            
    wb.save(response)
    
    return response