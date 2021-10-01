from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from datetime import date, datetime
from main.models import AnswersForFromSelf, AnswersForFromUs, SavedAnswers
from .models import Clicks
from .forms import ClicksForm
from member.models import UserInfo
from django.contrib.auth.decorators import login_required
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

def dashboard(request):
    today = date.today

    if request.user.is_superuser:
        message = "Originals Dashboard!"

        ## Persona type별 유저 수
        countAdam = UserInfo.objects.filter(persona_type='Adam').count()
        countBrian = UserInfo.objects.filter(persona_type='Brian').count()
        countClaire = UserInfo.objects.filter(persona_type='Claire').count()
        countOther = UserInfo.objects.filter(persona_type='Other').count()
        totalCountUsers = countAdam + countBrian + countClaire

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
        totalCountSelfs = countSelfByAdam + countSelfByBrian + countSelfByClaire

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
        totalCountUss = countUsByAdam + countUsByBrian + countUsByClaire

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
        totalBookmarks = countBookmarkByAdam + countBookmarkByBrian + countBookmarkByClaire

        ## 공개 Vs 미공개 컨텐츠 수
        allSelfsSharedFalse = AnswersForFromSelf.objects.filter(is_shared=False).count()
        allSelfsSharedTrue = AnswersForFromSelf.objects.filter(is_shared=True).count()
        allUssSharedFalse = AnswersForFromUs.objects.filter(is_shared=False).count()
        allUssSharedTrue = AnswersForFromUs.objects.filter(is_shared=True).count()

        sharedFalse = allSelfsSharedFalse + allUssSharedFalse
        sharedTrue = allSelfsSharedTrue + allUssSharedTrue
        totalAnswers = sharedFalse + sharedTrue

        ## Persona type별 클릭수
        personaOther = UserInfo.objects.filter(persona_type = 'Other').values('this_user')
        list__otherId = []
        for i in range(0, len(personaOther)):
            list__otherId.append(list(personaOther)[i]['this_user'])
        totalClicks = Clicks.objects.all().exclude(clicked_by__in=list__otherId).count()


        context = {
            'message' : message,
            'date' : today,

            'countAdam' : countAdam,
            'countBrian' : countBrian,
            'countClaire' : countClaire,
            'countOther' : countOther,
            'totalCountUsers' : totalCountUsers,

            'countSelfByAdam' : countSelfByAdam,
            'countSelfByBrian' : countSelfByBrian,
            'countSelfByClaire' : countSelfByClaire,
            'totalCountSelfs' : totalCountSelfs,

            'countUsByAdam' : countUsByAdam,
            'countUsByBrian' : countUsByBrian,
            'countUsByClaire' : countUsByClaire,
            'totalCountUss' : totalCountUss,

            'countBookmarkByAdam' : countBookmarkByAdam,
            'countBookmarkByBrian' : countBookmarkByBrian,
            'countBookmarkByClaire' : countBookmarkByClaire,
            'totalBookmarks' : totalBookmarks,

            'sharedFalse' : sharedFalse,
            'sharedTrue' : sharedTrue,
            'totalAnswers' : totalAnswers,

            'totalClicks' : totalClicks,
        }
    else:
        message = "관계자 외 출입 금지"
        context = {
            'message' : message
        }
    return render(request, 'dashboard/home.html', context)

