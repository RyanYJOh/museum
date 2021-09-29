from django.forms.widgets import RadioSelect
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import User
from .forms import QuestionsFromSelfForm, AnswersForFromUsForm, AnswersForFromSelfForm, SavedAnswersForm
from .models import QuestionsFromSelf, QuestionsFromUs, AnswersForFromSelf, AnswersForFromUs, SavedAnswers, RandomImages
from member.models import UserInfo
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import date, datetime
import json
import random

##### 공통 영역 #####
today = date.today()

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

def randImg():
    img_ids = RandomImages.objects.all().values_list('id', flat=True)
    list__img_ids = list(img_ids)
    
    random_img = random.choice(list__img_ids)
    return random_img

##### 홈 화면, 프로필 화면, About 화면 #####
def main_page(request):
    navbar_context = navbar(request)
    
    ## infiinte scroll을 할 것이냐, pagination을 쓸 것이냐.
    all_ans_us = AnswersForFromUs.objects.filter(is_shared=True).order_by('-created_at_time') 
    all_ans_self = AnswersForFromSelf.objects.filter(is_shared=True).order_by('-created_at_time')

    if request.user.is_authenticated:
        try:
            current_user = UserInfo.objects.get(this_user=request.user)

            ## 저장된 답변 가져오기
            us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_saved_by_user = list(us_saved_by_user)
            list__self_saved_by_user = list(self_saved_by_user)

            self_question_possible = 'True'

            pre_context = {
                'current_user' : current_user,
                'self_question_possible' : self_question_possible,
                'all_ans_us' : all_ans_us,
                'all_ans_self' : all_ans_self,
                'list__self_saved_by_user' : list__self_saved_by_user,
                'list__us_saved_by_user' : list__us_saved_by_user,
            }
        except ObjectDoesNotExist:
            return redirect('member/userinfo')

    else:
        current_user = ''
        self_question_possible = 'False'

        pre_context = {
            'all_ans_us' : all_ans_us,
            'all_ans_self' : all_ans_self,
            'current_user' : current_user,
            'self_question_possible' : self_question_possible,
        }

    context = {**navbar_context, **pre_context}
    return render(request, 'main/home.html', context)

def profile(request, username):
    navbar_context = navbar(request)
    from_profile_page = 'True'

    profile_owner = User.objects.get(username=username)
    
    ## 내 프로필
    if profile_owner == request.user:
        owner_info = UserInfo.objects.get(this_user=request.user)
        owner_ans_us = AnswersForFromUs.objects.filter(author_id=request.user).order_by('-created_at_time')
        if not owner_ans_us:
            owner_ans_us = 'None'
        else:
            pass
        owner_ans_self = AnswersForFromSelf.objects.filter(author_id=request.user).order_by('-created_at_time')
        if not owner_ans_self:
            owner_ans_self = "None"
        else:
            pass
        is_owner = 'True'
        
        ## 내가 저장한 글
        us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
        list__us_saved_by_user = list(us_saved_by_user)
        if not us_saved_by_user:
            list__us_bookmarked = "None"
        else:
            list__us_bookmarked = []
            for i in list__us_saved_by_user:
                new = AnswersForFromUs.objects.get(id=i)
                list__us_bookmarked.append(new)
        
        self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
        list__self_saved_by_user = list(self_saved_by_user)
        if not self_saved_by_user:
            list__self_bookmarked = "None"
        else:
            list__self_bookmarked = []
            for i in list__self_saved_by_user:
                new = AnswersForFromSelf.objects.get(id=i)
                list__self_bookmarked.append(new)

        pre_context = {
            'current_user' : request.user,
            'owner_info' : owner_info,
            'owner_ans_us' : owner_ans_us,
            'owner_ans_self' : owner_ans_self,
            'is_owner' : is_owner,
            # 'authenticated' : authenticated,
            'list__us_bookmarked' : list__us_bookmarked, 
            'list__self_bookmarked' : list__self_bookmarked,
            'list__us_saved_by_user' : list__us_saved_by_user,
            'list__self_saved_by_user' : list__self_saved_by_user,
            'from_profile_page' : from_profile_page,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/profile.html', context)
    
    ## 타인 프로필
    else:
        is_owner = 'False'

        ## 이 사람의 정답
        owner_ans_us = AnswersForFromUs.objects.filter(author_id=profile_owner, is_shared=True).order_by('-created_at_time')
        owner_ans_self = AnswersForFromSelf.objects.filter(author_id=profile_owner, is_shared=True).order_by('-created_at_time')
        
        if request.user.is_authenticated:
        ## 이 사람의 글 중 내가 저장한 글
            us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_saved_by_user = list(us_saved_by_user)
            list__self_saved_by_user = list(self_saved_by_user)

            pre_context = {
                'owner_info' : profile_owner.userinfo, 
                'owner_ans_us' : owner_ans_us,
                'owner_ans_self' : owner_ans_self,
                'list__us_saved_by_user' : list__us_saved_by_user,
                'list__self_saved_by_user' : list__self_saved_by_user,
                'is_owner' : is_owner,
                'from_profile_page' : from_profile_page,
            }
        else:
            pre_context = {
                'owner_info' : profile_owner.userinfo, 
                'owner_ans_us' : owner_ans_us,
                'owner_ans_self' : owner_ans_self,
                'is_owner' : is_owner,
                'from_profile_page' : from_profile_page,
            } 
        
        context = {**pre_context, **navbar_context}
        return render(request, 'main/profile.html', context)

def about(request):
    navbar_context = navbar(request)

    pre_context = {

    }

    context = {**navbar_context, **pre_context}
    return render(request, 'main/about.html', context)

##### 오늘 뮤지엄이 던지는 질문 #####
def create_ans_us_short(request):
    navbar_context = navbar(request)
    ## 로그인되어있는 경우와 아닌 경우 구분해야 함. 첫번째 질문에 한하여, 로그인 안되어 있어도 일단 답변은 가능. 하지만 곧바로 가입/로그인 유도해야 한다.
    if request.user.is_authenticated == False:
        today_ques = QuestionsFromUs.objects.get(question_no=1)
        # all_ans_for_this_ques = AnswersForFromUs.objects.select_related('author_id', 'author_id__userinfo').filter(question_no=1, is_shared=True)
        is_member = 'False'
        mode = 'create'

        pre_context = {
            'today_ques' : today_ques,
            # 'all_ans_for_this_ques' : all_ans_for_this_ques,
            'is_member' : is_member,
            'mode' : mode,
        }

        context = {**navbar_context, **pre_context}
        return render(request, 'main/C_ans_us.html', context)

    ## 로그인 되어 있는 경우
    elif request.user.is_authenticated:
        this_user = request.user
        today = date.today()
        is_member = "True"
        mode = 'create'

        ## 저장된 답변들 가져오기
        us_saved_by_user = SavedAnswers.objects.filter(bookmarker=this_user, ans_type='us').values_list('ans_us_ref', flat=True)
        list__us_saved_by_user = list(us_saved_by_user)
        self_saved_by_user = SavedAnswers.objects.filter(bookmarker=this_user, ans_type='us').values_list('ans_self_ref', flat=True)
        list__self_saved_by_user = list(self_saved_by_user)

        form = AnswersForFromUsForm(request.POST)
        ##### START 이 유저에게 할당된 오늘의 질문 가져오기 -> 즉문즉답에서 사용했던 로직 참고 #####
        ## 이 유저가 답변을 생성한 적이 없는 경우 (initial) => empty queryset
        if not AnswersForFromUs.objects.filter(author_id=request.user):
            # ans_formset = modelformset_factory(AnswersForFromUs, form=AnswersForFromUsForm, extra=1)
            
            ## 첫번째 질문 가져오기
            today_ques = QuestionsFromUs.objects.get(question_no=1)
            today_ques_id = today_ques.id
            ## 이건 today_ques_id의 답변들을 가져오는 코드
            all_ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=today_ques_id, is_shared=True).order_by('-created_at_time')
            if request.method == 'POST':
                form = AnswersForFromUsForm(request.POST)
                if form.is_valid(): ## 이거 괄호 없어도 되는 거 아녀?
                    instance = form.save(commit=False)
                    instance.author_id = request.user
                    instance.question_id = today_ques
                    instance.created_at = str(today)
                    random_image = RandomImages.objects.get(id=randImg())
                    instance.image = random_image.image

                    instance.save()
                    return redirect('/')
        
        ## 첫번째 질문에 답을 한 경우 (두번째 이후인 경우)
        else:
            ## 가장 최근 질문의 가장 최근 답변일 가져오기!!
            # 1) author_id의 모든 답변들의 question_id 가져오기
            answers_created = AnswersForFromUs.objects.filter(author_id=request.user).values('question_id') # QuerySet
            all_ques_ids = list(answers_created) # 딕셔너리가 들어있는 리스트 ----> 이것만 해도 충분하지 않음? instead of 아랫줄
            # all_ques_ids = list(answers_created.values('question_id')) # 딕셔너리가 들어있는 리스트
            # question_id 중 최댓값, 즉 답변을 한 가장 최근 질문의 id 가져오기
            list__ques_ids = []
            for i in range(0, len(all_ques_ids)): 
                list__ques_ids.append(*all_ques_ids[i].values()) # 여기 * operator는 python3 dictionary에 적용된 view?를 없애주는 것.
            latest_ques_id = max(list__ques_ids)

            # 2) author_id의, 가장 최근 질문의 가장 최근 created_at 가져오기
            latest_created_at = AnswersForFromUs.objects.filter(author_id=request.user, question_id=latest_ques_id).values('created_at')
            # all_created_ats의 각 원소는 {'created_at':datetime.date(2020, 07, 21)} 이런 포맷 (python dictionary view)
            all_created_ats = list(latest_created_at)
            # Date 중 최댓값, 즉 가장 최근의 질문의 날짜 가져오기 (바로 위와 정확히 동일)
            list__created_ats = []
            list__created_ats_in_format = []
            for j in range(0, len(all_created_ats)): 
                list__created_ats.append(*all_created_ats[j].values()) # 각 원소는 datetime.date(2020,07,21)의 포맷
                list__created_ats_in_format.append(list__created_ats[j].strftime('%Y-%m-%d')) # datetime.date(2020,07,21) -> 2020-07-21로 변환
            latest_created_at = max(list__created_ats)

            # 가장 최근 질문의 가장 최근 답변일이 가져와졌다. 이 날짜와 today의 값이 서로 같은지 다른지 확인해줘야 한다.
            # ans_formset = modelformset_factory(AnswersForFromUs, form=AnswersForFromUsForm, extra=1)
            if latest_created_at < today:
                # 다음 질문 가져오기 (정상적으로 진행)
                latest_ques = QuestionsFromUs.objects.get(id=latest_ques_id)
                today_ques_no = getattr(latest_ques, 'question_no')+1
                # formset = ans_formset(queryset=AnswersForFromUs.objects.filter(author_id = request.user, question_id=today_ques_no))
                today_ques = QuestionsFromUs.objects.get(question_no=today_ques_no)
                next_ques = QuestionsFromUs.objects.get(question_no = today_ques_no+1)

                ##  today_ques의 답변들을 가져와야 하는데, 그럼 먼저 today_ques의 id값을 알아야 한다.
                all_ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=today_ques.id, is_shared=True).order_by('-created_at_time')
                if request.method == "POST":
                    form = AnswersForFromUsForm(request.POST)
                    if form.is_valid():
                        instance = form.save(commit=False)
                        instance.author_id = request.user
                        instance.question_id = today_ques
                        instance.created_at = str(today)
                        random_image = RandomImages.objects.get(id=randImg())
                        instance.image = random_image.image

                        instance.save()

                        return redirect('/')

            ## 아직 날짜가 지나지 않았을 때 (수정만 가능함)
            elif latest_created_at == today:
                ## 오늘의 질문은 latest_ques와 같음
                latest_ques = QuestionsFromUs.objects.get(id=latest_ques_id)
                today_ques_no = getattr(latest_ques, 'question_no')
                today_ques = QuestionsFromUs.objects.get(question_no=today_ques_no)
                next_ques = QuestionsFromUs.objects.get(question_no = today_ques_no+1)

                all_ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=today_ques.id, is_shared=True).order_by('-created_at_time')
                my_ans_for_this_ques = AnswersForFromUs.objects.get(question_id=today_ques.id, author_id=this_user)
                message = "질문은 하루에 1개만 제공됩니다."
                next_ques_ready = 'False'
                        
                pre_context = {
                    'today_ques' : today_ques,
                    'all_ans_for_this_ques' : all_ans_for_this_ques,
                    'my_ans_for_this_ques' : my_ans_for_this_ques,
                    'message' : message,
                    'next_ques_ready' : next_ques_ready,
                    'next_ques' : next_ques,
                    'list__us_saved_by_user' : list__us_saved_by_user,
                    'list__self_saved_by_user' : list__self_saved_by_user,
                    'mode' : mode
                }

                context = {**pre_context, **navbar_context}
                return render(request, 'main/C_ans_us.html', context)
            ##### END 이 유저에게 할당된 오늘의 질문 가져오기 -> 즉문즉답에서 사용했던 로직 참고 #####

        pre_context = {
            'form' : form,
            'today_ques' : today_ques,
            'this_user' : this_user,
            'all_ans_for_this_ques' : all_ans_for_this_ques,
            'is_member' : is_member,
            'list__us_saved_by_user' : list__us_saved_by_user,
            'list__self_saved_by_user' : list__self_saved_by_user,
            'mode' : mode
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/C_ans_us.html', context)

def detail_ans_us(request, ans_us_id):
    navbar_context = navbar(request)

    this_ans = AnswersForFromUs.objects.get(id=ans_us_id)
    if request.user.is_authenticated:
        ## 북마크
        if SavedAnswers.objects.filter(ans_us_ref=this_ans, bookmarker=request.user).exists():
            bookmarked = 'True'
        else:
            bookmarked = 'False'

        if this_ans.author_id == request.user:
            editable = 'True'
        else:
            editable = ''
        
    else:
        editable = ''
        bookmarked = ''

    pre_context = {
        'this_ans' : this_ans,
        'editable' : editable,
        'bookmarked' : bookmarked
    }

    context = {**pre_context, **navbar_context}
    return render(request, 'main/D_ans_us.html', context)

@login_required(login_url="/login")
def update_ans_us(request, ans_us_id):
    navbar_context = navbar(request)

    ans_to_update = AnswersForFromUs.objects.get(id = ans_us_id)
    this_question = QuestionsFromUs.objects.get(id=ans_to_update.question_id.id)
    mode = 'update'
    ans_form = AnswersForFromUsForm(request.POST, request.FILES)
    if request.method == 'POST':
        if ans_form.is_valid():
            ## POST된 ans_form 받아다가, 그 안의 데이터를 ans_to_update에 넣어주고 저장.
            ## 기존처럼 삭제하고 다시 save하는 구조 아님!
            ans_instance = ans_form.save(commit=False)
            ans_to_update.updated_at = str(today)
            ans_to_update.body = ans_instance.body
            ans_to_update.is_shared = ans_instance.is_shared

            ans_to_update.save()
            ans_us_id = ans_to_update.id
            
        return redirect('/originals-answer/{ans_id}'.format(ans_id=ans_us_id))

    ## 수정하기 위해 페이지 진입
    else:
        form = AnswersForFromUsForm(instance=ans_to_update)
        pre_context = {
            'form' : form,
            'this_question' : this_question,
            'mode' : mode
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/C_ans_us.html', context)

##### 내가 나에게 던지는 질문 #####
def create_ans_self(request):
    navbar_context = navbar(request)
    today = date.today()

    ques_form = QuestionsFromSelfForm(request.POST, request.FILES)
    ans_form = AnswersForFromSelfForm(request.POST)
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST': 
            ## Question 먼저 validate
            if ques_form.is_valid():
                ques_instance = ques_form.save(commit=False)
                if ques_form.cleaned_data.get('image'):
                    pass
                else:
                    random_image = RandomImages.objects.get(id=randImg())
                    ques_instance.image = random_image.image
                    
                    
                ques_instance.save()

                ## Answer validation
                if ans_form.is_valid():
                    ans_instance = ans_form.save(commit=False)
                    ans_instance.question_id = ques_instance
                    ans_instance.author_id = current_user
                    ans_instance.updated_at = str(today)
                    
                    ans_instance.save()
                    
                    ans_self_id = ans_instance.id

                return redirect('/self-answer/{ans_id}'.format(ans_id=ans_self_id))

        mode = 'create'
        pre_context = {
            'ques_form' : ques_form,
            'ans_form' : ans_form,
            'mode' : mode
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/C_ans_self.html', context)
    
    ## 비로그인 유저
    else:
        message = "...은 로그인을 한 뒤에 이용할 수 있어요."
        pre_context = {
            'message' : message,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/C_ans_self.html', context)

def detail_ans_self(request, ans_self_id):
    navbar_context = navbar(request)

    this_ans = AnswersForFromSelf.objects.get(id=ans_self_id)
    if request.user.is_authenticated:
        ## 북마크
        if SavedAnswers.objects.filter(ans_self_ref=this_ans, bookmarker=request.user).exists():
            bookmarked = 'True'
        else: 
            bookmarked = 'False'

        ## 수정하기
        if this_ans.author_id == request.user:
            editable = 'True'
        else:
            editable = ''

    else: 
        editable = ''
        bookmarked = ''

    pre_context = {
        'this_ans' : this_ans,
        'editable' : editable,
        'bookmarked' : bookmarked,
    }

    context = {**pre_context, **navbar_context}
    return render(request, 'main/D_ans_self.html', context)

@login_required(login_url="/login")
def update_ans_self(request, ans_self_id):
    navbar_context = navbar(request)

    ans_to_update = AnswersForFromSelf.objects.get(id = ans_self_id)
    ques_to_update = QuestionsFromSelf.objects.get(id=ans_to_update.question_id.id)

    ques_form = QuestionsFromSelfForm(request.POST, request.FILES)
    ans_form = AnswersForFromSelfForm(request.POST, request.FILES)
    if request.method == 'POST':
        if ques_form.is_valid():
            ques_instance = ques_form.save(commit=False)
            ques_to_update.title = ques_instance.title
            if ques_instance.image:
                ques_to_update.image = ques_instance.image
            else:
                pass
            
            ques_to_update.save()

        if ans_form.is_valid():
            ans_instance = ans_form.save(commit=False)
            ans_to_update.updated_at = str(today)
            ans_to_update.subtitle = ans_instance.subtitle
            ans_to_update.body = ans_instance.body
            # ans_to_update.image = ans_instance.image
            ans_to_update.is_shared = ans_instance.is_shared

            ans_to_update.save()

            ans_self_id = ans_to_update.id

        return redirect('/self-answer/{ans_id}'.format(ans_id=ans_self_id))

    ## 수정하기 위해 페이지 진입
    else:
        mode = 'update'
        ques_form = QuestionsFromSelfForm(instance=ques_to_update)
        ans_form = AnswersForFromSelfForm(instance=ans_to_update)
        pre_context = {
            'ques_form' : ques_form,
            'ans_form' : ans_form,
            'mode' : mode,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/C_ans_self.html', context)

##### 매거진 메인 화면 #####


##### 매거진 디테일 화면 #####

##### 답변 저장 기능 #####
def bookmark(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        ans_type = data['ans_type']
        ans_us_ref = data['ans_us_ref']
        ans_self_ref = data['ans_self_ref']
        if request.method == 'POST':
            form = SavedAnswersForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                ## 현재 북마크한 놈이 이미 DB에 존재할 때는 삭제
                if ans_self_ref == '' and SavedAnswers.objects.filter(ans_type=ans_type, ans_us_ref=ans_us_ref, bookmarker=request.user).exists(): ## Somehow, .get()을 쓰면 exists()가 안된다.
                    print('해당 뮤지엄 질문은 이미 존재합니다')
                    SavedAnswers.objects.get(ans_type=ans_type, ans_us_ref=ans_us_ref, bookmarker=request.user).delete()

                    ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                    return redirect('/me')
                elif ans_us_ref == '' and SavedAnswers.objects.filter(ans_type=ans_type, ans_self_ref=ans_self_ref, bookmarker=request.user).exists(): ## Somehow, .get()을 쓰면 exists()가 안된다.
                    print('해당 나에게 질문은 이미 존재합니다')
                    SavedAnswers.objects.get(ans_type=ans_type, ans_self_ref=ans_self_ref, bookmarker=request.user).delete()

                    ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                    return redirect('/me')

                ## 그렇지 않은 경우에는 저장
                else:
                    instance.ans_type = ans_type
                    if ans_type == 'us':
                        instance.ans_us_ref = AnswersForFromUs.objects.get(id=ans_us_ref) 
                    elif ans_type == 'self':
                        instance.ans_self_ref = AnswersForFromSelf.objects.get(id=ans_self_ref) 
                    instance.bookmarker = request.user
            
                    instance.save()
                    print(instance.ans_type, instance.ans_self_ref, instance.ans_us_ref, instance.bookmarker)
                    
                    ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                    return redirect('/me')
            else:
                print('@@@@@@ Validation failed due to : ', form.errors)
    else:
        pass


def csrf_failure(request, reason=""):
    context = {
        'message' : 'sorry'
    }
    return render(request, 'main/csrf_failure.html', context)
