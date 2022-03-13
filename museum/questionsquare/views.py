from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from main.views import navbar, randImg
from main.models import RandomImages
from .forms import QuestionsFromOthersForm, AnswersForFromOthersForm
from .models import QuestionsFromOthers, AnswersForFromOthers
from member.models import UserInfo
from django.db.models import Count
import random

# Create your views here.
def get_today():
    now = timezone.now()
    string__today = str(now).split()[0]
    today = datetime.strptime(string__today, '%Y-%m-%d').date()

    return today

## 타던질 메인
def question_square(request):
    navbar_context = navbar(request)

    questions = QuestionsFromOthers.objects.all().order_by('-created_at_time').annotate(
        count_answers = Count('answersforfromothers')
    )
    # answers = AnswersForFromOthers.objects.all()

    if request.user.is_authenticated:
        user_authenticated = True
    else:
        user_authenticated = False

    pre_context = {
        'questions' : questions,
        # 'answers' : answers,
        'user_authenticated' : user_authenticated,
    }

    context = {**pre_context, **navbar_context}

    return render(request, 'questionsquare/home.html', context)

## Create 질문
@login_required(login_url="/login")
def create_ques_from_others(request):
    navbar_context = navbar(request)
    
    ## 랜덤 이모지
    list__rand_emoji = [
        "🤸‍♂️",'✍','🎈','🎠','🎨',
        '🎲','🧩','🧸','🎸','🎹',
        '📕','📚','💡','📌','🍕',
        '🍔','🌭','🍞','🌮','🌯',
        '🥗','☕','🥑','🥕','🌳'
    ]
    rand_emoji = random.choice(list__rand_emoji)

    ques_form = QuestionsFromOthersForm(request.POST, request.FILES)
    if request.user.is_authenticated:
        current_user = UserInfo.objects.get(this_user=request.user)
        if request.method == 'POST':
            if ques_form.is_valid():
                ques_instance = ques_form.save(commit=False)
                
                ques_instance.title = rand_emoji + " " + ques_instance.title
                ques_instance.questioner = current_user
                ques_instance.save()

                ques_id = ques_instance.id
            return redirect('answers-of/{ques_id}'.format(ques_id=ques_id))

        mode = 'create'
        pre_context = {
            'ques_form' : ques_form,
            'mode' : mode
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'questionsquare/C_ques_others.html', context)
    
    ## 비로그인 유저
    else:
        message = "...은 로그인을 한 뒤에 이용할 수 있어요."
        pre_context = {
            'message' : message,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'questionsquare/C_ques_others.html', context)

## Update 질문
@login_required(login_url="/login")
def update_ques_from_others(request, ques_others_id):
    navbar_context = navbar(request)

    ques_to_update = QuestionsFromOthers.objects.get(id=ques_others_id)
    ques_form = QuestionsFromOthersForm(request.POST, request.FILES)

    if request.method == 'POST':
        if ques_form.is_valid():
            ques_instance = ques_form.save(commit=False)
            ques_to_update.title = ques_instance.title
            if ques_instance.image:
                ques_to_update.image = ques_instance.image
            else:
                pass
            
            ques_to_update.title = ques_instance.title
            ques_to_update.desc = ques_instance.desc
            
            ques_to_update.save()

        return redirect('/question-square/answers-of/{ques_id}'.format(ques_id=ques_others_id))

    ## 수정하기 위해 페이지 진입
    else:
        mode = 'update'
        ques_form = QuestionsFromOthersForm(instance=ques_to_update)
        pre_context = {
            'ques_form' : ques_form,
            'mode' : mode,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'questionsquare/C_ques_others.html', context)

## Delete 질문
@login_required(login_url="/login")
def delete_ques_from_others(request, ques_others_id):
    this_ques = QuestionsFromOthers.objects.get(id=ques_others_id)
    
    if UserInfo.objects.get(this_user=request.user) == this_ques.questioner:
        this_ques.delete()
    else:
        pass
    return redirect('/question-square')

## 답변 목록
def view_ans_others(request, ques_id):
    navbar_context = navbar(request)

    ans_for_this_ques = AnswersForFromOthers.objects.filter(question_id=ques_id).order_by('-created_at_time')
    this_question = QuestionsFromOthers.objects.get(id=ques_id)
    
    ## 질문 주인 여부 (수정/삭제)
    if this_question.questioner.this_user == request.user:
        is_ques_owner = True
        print('true')
    else:
        is_ques_owner = False
        print('false')

    ## 발제자 프로필
    this_questioner = this_question.questioner

    ## 답변 있는지 여부 먼저 체크해야됨.
    if ans_for_this_ques:
        
        pre_context = {
            'exists' : True,
            'this_questioner' : this_questioner,
        }
    else: 
        pre_context = {
            'exists' : False,
            'this_questioner' : this_questioner,
        }
    
    pre_context['ans_for_this_ques'] = ans_for_this_ques
    pre_context['this_question'] = this_question
    pre_context['is_ques_owner'] = is_ques_owner

    context = {**pre_context, **navbar_context}
    return render(request, 'questionsquare/answers.html', context)

## Create 타던질 답변
@login_required(login_url="/login")
def create_ans_others(request, ques_others_id):
    navbar_context = navbar(request)

    this_ques = QuestionsFromOthers.objects.get(id=ques_others_id)
    ans_form = AnswersForFromOthersForm(request.POST, request.FILES)
    if request.user.is_authenticated:
        is_member = True
        current_user = request.user
        if request.method == 'POST':
            if ans_form.is_valid():
                ans_intstance = ans_form.save(commit=False)
                if ans_form.cleaned_data.get('image'):
                    pass
                else:
                    random_image = RandomImages.objects.get(id=randImg())
                    ans_intstance.image = random_image.image
                
                ans_intstance.question_id = this_ques
                ans_intstance.author = UserInfo.objects.get(this_user=current_user)
                ans_intstance.save()

            return redirect('/question-square/answers-of/{ques_id}'.format(ques_id=ques_others_id))

        mode = 'create'
        pre_context = {
            'ans_form' : ans_form,
            'mode' : mode,
            'this_ques' : this_ques,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'questionsquare/C_ans_others.html', context)
    
    ## 비로그인 유저
    else:
        is_member = False
        pre_context = {
            'is_member' : is_member,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'questionsquare/C_ans_others.html', context)

## 답변 detail
def detail_ans_others(request, ans_others_id):
    navbar_context = navbar(request)

    this_ans = AnswersForFromOthers.objects.get(id=ans_others_id)
    this_ques_id = this_ans.question_id.id
    this_ques = QuestionsFromOthers.objects.get(id=this_ques_id)
    
    if request.user.is_authenticated:
        ## 수정하기
        if this_ans.author == UserInfo.objects.get(this_user=request.user):
            editable = 'True'
        else:
            editable = ''
        if request.user:
            current_user = UserInfo.objects.get(this_user=request.user)
        else:
            current_user = ''
    else: 
        editable = ''
        # bookmarked = ''
        current_user = ''

    ## 다른 답변들 노출
    all_ans_others = AnswersForFromOthers.objects.filter(question_id=this_ques_id).exclude(id=ans_others_id).order_by('-created_at_time')

    pre_context = {
        'this_ans' : this_ans,
        'editable' : editable,
        # 'bookmarked' : bookmarked,
        'all_ans_others' : all_ans_others,
        'ans_others_id' : ans_others_id,
        'current_user' : current_user,
        'this_ques' : this_ques,
    }

    context = {**pre_context, **navbar_context}
    return render(request, 'questionsquare/D_ans_others.html', context)

## 답변 수정
@login_required(login_url="/login")
def update_ans_others(request, ans_others_id):
    navbar_context = navbar(request)

    ans_to_update = AnswersForFromOthers.objects.get(id=ans_others_id)
    ans_form = AnswersForFromOthersForm(request.POST, request.FILES)
    
    this_ques = QuestionsFromOthers.objects.get(id=ans_to_update.question_id.id)

    if request.method == 'POST':
        if ans_form.is_valid():
            ans_instance = ans_form.save(commit=False)
            if ans_instance.image:
                ans_to_update.image = ans_instance.image
            else:
                pass
            
            ans_to_update.body = ans_instance.body
            ans_to_update.save()

        return redirect('/question-square/answer/{ans_id}'.format(ans_id=ans_others_id))

    ## 수정하기 위해 페이지 진입
    else:
        mode = 'update'
        ans_form = AnswersForFromOthersForm(instance=ans_to_update)
        pre_context = {
            'ans_form' : ans_form,
            'mode' : mode,
            'this_ques' : this_ques,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'questionsquare/C_ans_others.html', context)

## 답변 삭제
@login_required(login_url="/login")
def delete_ans_others(request, ans_others_id):
    this_ans = AnswersForFromOthers.objects.get(id=ans_others_id)
    this_ques = QuestionsFromOthers.objects.get(id=this_ans.question_id.id)

    if UserInfo.objects.get(this_user=request.user) == this_ans.author:
        this_ans.delete()
    else:
        pass
    return redirect('/question-square/answers-of/{ques_id}'.format(ques_id=this_ques.id))
