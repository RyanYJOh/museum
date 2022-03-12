from django.forms.widgets import RadioSelect
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.views.generic import FormView
from django.contrib.auth.models import User

from questionsquare.models import QuestionsFromOthers
from .forms import CommentAnsUsForm, CommentAnsSelfForm, QuestionsFromSelfForm, AnswersForFromUsForm, AnswersForFromSelfForm, SavedAnswersForm, SearchForm, LikesForm
from .models import CommentAnsUs, CommentAnsSelf, QuestionsFromSelf, QuestionsFromUs, AnswersForFromSelf, AnswersForFromUs, SavedAnswers, RandomImages, Likes, Notice
from member.models import UserInfo, UserInfoAdditional
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime
import json
import random
from django.core.paginator import Paginator
from django.db.models import Count
from itertools import chain

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
                'navbar_authenticated' : navbar_authenticated,
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

##### 검색 #####

def home_search(form):
    if form.is_valid():
        keyword = form.cleaned_data['search_keyword']
        which = form.cleaned_data['which']

        if which == 'answer':    
            all_ans_us = AnswersForFromUs.objects.filter(Q(body__icontains=keyword) & Q(is_shared=True)).distinct().order_by('-created_at_time').annotate(
            count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
            )

            all_ans_self = AnswersForFromSelf.objects.filter(Q(body__icontains=keyword) & Q(is_shared=True)).distinct().order_by('-created_at_time').annotate(
            count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
            )

            context = {
                'search_form' : form,
                'keyword' : keyword,
                'all_ans_us' : all_ans_us,
                'all_ans_self' : all_ans_self,
            }

        elif which == 'question' :
            us_ques_list = QuestionsFromUs.objects.filter(Q(title__icontains=keyword) | Q(body__icontains=keyword)).distinct().values_list('pk', flat=True)
            print('us_ques_list : ', us_ques_list)
            all_ans_us = AnswersForFromUs.objects.filter(is_shared=True, question_id__in=us_ques_list).order_by('-created_at_time').annotate(
                count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
            )
            self_ques_list = QuestionsFromSelf.objects.filter(Q(title__icontains=keyword)).distinct().values_list('pk', flat=True)
            print('self_ques_list : ', self_ques_list)
            all_ans_self = AnswersForFromSelf.objects.filter(is_shared=True, question_id__in=self_ques_list).order_by('-created_at_time').annotate(
                count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
            )
            
            print('all_ans_us : ', all_ans_us)
            print('all_ans_self : ', all_ans_self)

            context = {
                'search_form' : form,
                'keyword' : keyword,
                'all_ans_us' : all_ans_us,
                'all_ans_self' : all_ans_self,
            }

        elif which == 'user':
            user_list = UserInfo.objects.filter(Q(real_name__icontains=keyword) | Q(self_intro__icontains=keyword)).distinct().values_list('this_user', flat=True)
            all_ans_us = AnswersForFromUs.objects.filter(is_shared=True, author_id__in=user_list).order_by('-created_at_time').annotate(
                count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
            )
            all_ans_self = AnswersForFromSelf.objects.filter(is_shared=True, author_id__in=user_list).order_by('-created_at_time').annotate(
                count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
            )

            context = {
                'search_form' : form,
                'keyword' : keyword,
                'all_ans_us' : all_ans_us,
                'all_ans_self' : all_ans_self,
            }

        return context
    else:
        pass

##### 홈 화면, 프로필 화면, About 화면 #####
def d__________main_page(request):
    navbar_context = navbar(request)

    
    ## 답변 리스트 쿼리 -- 검색결과인지 여부 먼저 확인해야 함
    search_form = SearchForm(request.POST)
    print('METHOD.POST : ', request.POST)
    print('METHOD IS :  ', request.method)
    if request.method == 'POST':
        search_context = home_search(search_form)
        print('SEARCH RESULT : ', search_context)
        all_ans_us = search_context['all_ans_us']
        all_ans_self = search_context['all_ans_self']
        is_search_result=True
    else:
        all_ans_us = AnswersForFromUs.objects.filter(is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
        )
        all_ans_self = AnswersForFromSelf.objects.filter(is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
        )
        is_search_result=False

    ## Pagination
    paginator_all_ans_us = Paginator(all_ans_us, 12)   
    page_all_ans_us = request.GET.get('page')
    all_ans_us_paginated = paginator_all_ans_us.get_page(page_all_ans_us)

    paginator_all_ans_self = Paginator(all_ans_self, 12)
    page_all_ans_self = request.GET.get('page')   
    all_ans_self_paginated = paginator_all_ans_self.get_page(page_all_ans_self)

    ## [질문 모아보기]를 위해 지금까지 답변된 질문들 가져오기
    list__ques_id_answered_sofar = list(all_ans_us.values_list('question_id', flat=True))
    ques_no_answered_sofar = QuestionsFromUs.objects.filter(id__in=list__ques_id_answered_sofar).values('question_no', 'title').order_by('-question_no')

    ## user authentication
    if request.user.is_authenticated:
        ## UserInfo 작성했는지 확인
        try:
            current_user = UserInfo.objects.get(this_user=request.user)

            ## 저장된 답변 가져오기
            us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_saved_by_user = list(us_saved_by_user)
            list__self_saved_by_user = list(self_saved_by_user)

            ## 이건 뭐임?
            self_question_possible = 'True'

            pre_context = {
                'search_form' : search_form,
                'current_user' : current_user,
                'self_question_possible' : self_question_possible,
                'all_ans_us' : all_ans_us,
                'all_ans_self' : all_ans_self,
                'list__self_saved_by_user' : list__self_saved_by_user,
                'list__us_saved_by_user' : list__us_saved_by_user,
                'ques_no_answered_sofar' : ques_no_answered_sofar,
                'all_ans_us_paginated' : all_ans_us_paginated,
                'all_ans_self_paginated' : all_ans_self_paginated,
                'is_search_result' : is_search_result,
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
            'ques_no_answered_sofar' : ques_no_answered_sofar,
            'self_question_possible' : self_question_possible,
            'all_ans_us_paginated' : all_ans_us_paginated,
            'all_ans_self_paginated' : all_ans_self_paginated,
            'is_search_result' : is_search_result,
        }

    context = {**navbar_context, **pre_context}
    return render(request, 'main/v2__home.html', context)
 
def main_page(request):
    navbar_context = navbar(request)
    
    ## 답변 리스트 쿼리 -- 검색결과인지 여부 먼저 확인해야 함
    search_form = SearchForm(request.POST)
    print('METHOD.POST : ', request.POST)
    print('METHOD IS :  ', request.method)

    if request.method == 'POST':    ## 검색 결과임
        is_search_result=True

        search_context = home_search(search_form)
        all_ans_us = search_context['all_ans_us']
        all_ans_self = search_context['all_ans_self']

    else:   ## 검색 결과 아님 (최초 진입)
        is_search_result=False

        all_ans_us = AnswersForFromUs.objects.filter(is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansus'), ## annotate은 댓글 갯수 가져오는 용도.
        )
        all_ans_self = AnswersForFromSelf.objects.filter(is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansself'), ## annotate은 댓글 갯수 가져오는 용도.
        )

    ## 화면에 뿌려주기.. 
    ## 문제는, 서로 다른 모델의 queryset을 합쳐서(merge) 보여줘야 한다는 것.
    ## See : https://howchoo.com/django/combine-two-querysets-with-different-models
    ## 근데 아래 방법으로 하면 performance가 현저히 낮아진다고 함. 특히 queryset이 커짐에 따라.
    all_answers = sorted(
        chain(all_ans_us, all_ans_self),
        key=lambda post: post.created_at_time, reverse=True
    )

    ## Pagination
    paginator_answers = Paginator(all_answers, 10)
    page_all_answers = request.GET.get('page')
    all_answers_paginated = paginator_answers.get_page(page_all_answers)

    ## [질문 모아보기] 필터를 위해 지금까지 답변된 질문들 가져오기
    list__ques_id_answered_sofar = list(all_ans_us.values_list('question_id', flat=True))
    ques_no_answered_sofar = QuestionsFromUs.objects.filter(id__in=list__ques_id_answered_sofar).values('question_no', 'title').order_by('-question_no').annotate(
        count_answers = Count('answerforfromus')
    )

    ## 스퀘어 질문들 5개 가져오기
    square = QuestionsFromOthers.objects.all().order_by('-created_at')[:5].annotate(
        count_answers = Count('answersforfromothers'), ## annotate은 댓글 갯수 가져오는 용도.
    )

    ## user authentication
    if request.user.is_authenticated:
        ## UserInfo 작성했는지 확인
        try:
            current_user = UserInfo.objects.get(this_user=request.user)

            ## 저장된 답변 가져오기
            us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_saved_by_user = list(us_saved_by_user)
            list__self_saved_by_user = list(self_saved_by_user)

            ## Like한 답변 가져오기
            us_liked_by_user = Likes.objects.filter(liker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_liked_by_user = Likes.objects.filter(liker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_liked_by_user = list(us_liked_by_user)
            list__self_liked_by_user = list(self_liked_by_user)

            ## 나에게 던지는 질문 가능 (로그인 됨)
            self_question_possible = 'True'

            pre_context = {
                'request_user' : request.user.id,
                'search_form' : search_form,
                'current_user' : current_user,
                'self_question_possible' : self_question_possible,
                'all_ans_us' : all_ans_us,
                'all_ans_self' : all_ans_self,
                'list__self_saved_by_user' : list__self_saved_by_user,
                'list__us_saved_by_user' : list__us_saved_by_user,
                'list__us_liked_by_user' : list__us_liked_by_user,
                'list__self_liked_by_user' : list__self_liked_by_user,
                'ques_no_answered_sofar' : ques_no_answered_sofar,
                'all_answers' : all_answers_paginated,
                'is_search_result' : is_search_result,
                'square' : square,
            }
        except ObjectDoesNotExist:
            return redirect('member/userinfo')

    else:
        current_user = ''
        self_question_possible = 'False'

        pre_context = {
            'request_user' : 0,
            'all_ans_us' : all_ans_us,
            'all_ans_self' : all_ans_self,
            'current_user' : current_user,
            'ques_no_answered_sofar' : ques_no_answered_sofar,
            'self_question_possible' : self_question_possible,
            # 'all_ans_us_paginated' : all_ans_us_paginated,
            # 'all_ans_self_paginated' : all_ans_self_paginated,
            'all_answers' : all_answers_paginated,
            'is_search_result' : is_search_result,
            'square' : square,
        }

    context = {**navbar_context, **pre_context}
    return render(request, 'main/v2__home.html', context)

def main_page_filtered(request, question_no):
    navbar_context = navbar(request)
    
    ## Pagination을 쓸 것이냐.
    this_question = QuestionsFromUs.objects.get(question_no=question_no).pk
    all_ans_us_filtered = AnswersForFromUs.objects.filter(is_shared=True, question_id=this_question).order_by('-created_at_time').annotate(
        count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
    )
    paginator_all_ans_us = Paginator(all_ans_us_filtered, 12)
    page_all_ans_us = request.GET.get('page')
    all_ans_us_paginated = paginator_all_ans_us.get_page(page_all_ans_us)

    all_ans_self = AnswersForFromSelf.objects.filter(is_shared=True).order_by('-created_at_time').annotate(
        count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
    )
    paginator_all_ans_self = Paginator(all_ans_self, 12)
    page_all_ans_self = request.GET.get('page')
    all_ans_self_paginated = paginator_all_ans_self.get_page(page_all_ans_self)
    
    ## [질문 모아보기]를 위해 지금까지 답변된 질문들 가져오기
    all_ans_us = AnswersForFromUs.objects.filter(is_shared=True).order_by('-created_at_time') 
    list__ques_id_answered_sofar = list(all_ans_us.values_list('question_id', flat=True))
    ques_no_answered_sofar = QuestionsFromUs.objects.filter(id__in=list__ques_id_answered_sofar).values('question_no', 'title').order_by('question_no')
    
    ## 스퀘어 질문들 5개 가져오기
    square = QuestionsFromOthers.objects.all().order_by('-created_at')[:5]

    ## user authentication
    if request.user.is_authenticated:
        ## UserInfo 작성했는지 확인
        try:
            current_user = UserInfo.objects.get(this_user=request.user)

            ## 저장된 답변 가져오기
            us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_saved_by_user = list(us_saved_by_user)
            list__self_saved_by_user = list(self_saved_by_user)

            ## 이건 뭐임?
            self_question_possible = 'True'

            pre_context = {
                'current_user' : current_user,
                'self_question_possible' : self_question_possible,
                'all_ans_us_filtered' : all_ans_us_filtered,
                'all_ans_self' : all_ans_self,
                'list__self_saved_by_user' : list__self_saved_by_user,
                'list__us_saved_by_user' : list__us_saved_by_user,
                'ques_no_answered_sofar' : ques_no_answered_sofar,
                'all_ans_us_paginated' : all_ans_us_paginated,
                'all_ans_self_paginated' : all_ans_self_paginated,
                'square' : square,
            }
        except ObjectDoesNotExist:
            return redirect('member/userinfo')

    else:
        current_user = ''
        self_question_possible = 'False'

        pre_context = {
            'all_ans_us_filtered' : all_ans_us_filtered,
            'all_ans_self' : all_ans_self,
            'current_user' : current_user,
            'self_question_possible' : self_question_possible,
            'ques_no_answered_sofar' : ques_no_answered_sofar,
            'all_ans_us_paginated' : all_ans_us_paginated,
            'all_ans_self_paginated' : all_ans_self_paginated,
            'square' : square,
        }

    context = {**navbar_context, **pre_context}
    return render(request, 'main/home_filtered.html', context)

def detail_modal(request, ques_from, id):
    if ques_from == 'originals':
        this_ans = AnswersForFromUs.objects.filter(id=id).values()
        title = QuestionsFromUs.objects.filter(id=this_ans[0]['question_id_id']).values('title')[0]['title']
        img = this_ans[0]['image']
    elif ques_from == 'self':
        this_ans = AnswersForFromSelf.objects.filter(id=id).values()
        this_ques = QuestionsFromSelf.objects.filter(id=this_ans[0]['question_id_id']).values('title', 'image')
        title = this_ques[0]['title'] 
        img = this_ques[0]['image'] 
    
    author = UserInfo.objects.filter(this_user=this_ans[0]['author_id_id']).values('real_name', 'profile_image')
    username = User.objects.filter(id=this_ans[0]['author_id_id']).values('username')[0]['username']
    
    author_name = author[0]['real_name']
    created_at = this_ans[0]['created_at']
    body = this_ans[0]['body']
    author_img = author[0]['profile_image']
    

    # img 이름이 media/로 시작하면 : 사용자가 직접 등록한 이미지
    # 그렇지 않으면 : 디폴트 이미지
    if author_img.split('/')[0] == 'media':
        profile_img_media_url = 'https://res.cloudinary.com/he2prkoby/image/upload/v1/'

    else:
        profile_img_media_url = '/media/'

    
    if img.split('/')[0] == 'media':
        detail_img_media_url = 'https://res.cloudinary.com/he2prkoby/image/upload/v1/'

    else:
        detail_img_media_url = '/media/'


    dict__detail = {
        'id' : id,
        'title' : title,
        'author' : author_name,
        'profile_img' : profile_img_media_url+author_img,
        'created_at' : created_at,
        'img' : detail_img_media_url+img,
        'body' : body,
        'username' : username,
    }
    print(dict__detail)

    # print(dict__detail)
    result = json.dumps(dict__detail, default=str)
    return HttpResponse(result, content_type="text/json") # charset=utf8 필요?

def d_____profile(request, username):
    navbar_context = navbar(request)
    from_profile_page = 'True'

    profile_owner = User.objects.get(username=username)
    
    ## 내 프로필
    if profile_owner == request.user:
        owner_info = UserInfo.objects.get(this_user=request.user)
        owner_ans_us = AnswersForFromUs.objects.filter(author_id=request.user).order_by('-created_at_time').annotate(
            count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
        )
        if not owner_ans_us:
            owner_ans_us = 'None'
        else:
            pass

        owner_ans_self = AnswersForFromSelf.objects.filter(author_id=request.user).order_by('-created_at_time').annotate(
            count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
        )
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
            'list__us_bookmarked' : list__us_bookmarked, 
            'list__self_bookmarked' : list__self_bookmarked,
            'list__us_saved_by_user' : list__us_saved_by_user,
            'list__self_saved_by_user' : list__self_saved_by_user,
            'from_profile_page' : from_profile_page,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/v2__profile.html', context)
    
    ## 타인 프로필
    else:
        is_owner = 'False'

        ## 이 사람의 정답
        owner_ans_us = AnswersForFromUs.objects.filter(author_id=profile_owner, is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
        )
        owner_ans_self = AnswersForFromSelf.objects.filter(author_id=profile_owner, is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
        )
        
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

def profile(request, username):
    navbar_context = navbar(request)
    from_profile_page = 'True'

    profile_owner = User.objects.get(username=username)

    ##### 전체 공개되는 컨텐츠 #####
    ## 1. UserInfoAdditional
    try:
        this_userinfoadditional = UserInfoAdditional.objects.get(this_user=profile_owner)
    except ObjectDoesNotExist:
        return redirect('/member/edit-userinfo/'+username)
    ###############################

    ## 내 프로필
    if profile_owner == request.user:
        is_owner = True

        owner_info = UserInfo.objects.get(this_user=request.user)
        owner_ans_us = AnswersForFromUs.objects.filter(author_id=request.user).order_by('-created_at_time').annotate(
            count_comments = Count('commentansus', distinct=True), ## annotate은 댓글 갯수 가져오는 용도.
            count_likes = Count('likesUs', distinct=True)
        )
        
        owner_ans_self = AnswersForFromSelf.objects.filter(author_id=request.user).order_by('-created_at_time').annotate(
            count_comments = Count('commentansself', distinct=True), ## annotate은 댓글 갯수 가져오는 용도.
            count_likes = Count('likesSelf', distinct=True)
        )

        ## 문제는, 서로 다른 모델의 queryset을 합쳐서(merge) 보여줘야 한다는 것.
        ## See : https://howchoo.com/django/combine-two-querysets-with-different-models
        ## 근데 아래 방법으로 하면 performance가 현저히 낮아진다고 함. 특히 queryset이 커짐에 따라.
        all_answers = sorted(
            chain(owner_ans_self, owner_ans_us),
            key=lambda post: post.created_at_time, reverse=True
        )

        ## Pagination -> 일단 hold
        paginator_answers = Paginator(all_answers, 10)
        page_all_answers = request.GET.get('page')
        all_answers_paginated = paginator_answers.get_page(page_all_answers)
        
        ## 북마크한 글
        us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
        list__us_saved_by_user = AnswersForFromUs.objects.filter(id__in=us_saved_by_user)
        
        self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
        list__self_saved_by_user = AnswersForFromSelf.objects.filter(id__in=self_saved_by_user)

        ## 두 queryset 합쳐주기
        all_bookmarked = sorted(
            chain(list__us_saved_by_user, list__self_saved_by_user),
            key=lambda post: post.created_at_time, reverse=True
        )

        pre_context = {
            'current_user' : request.user,
            'owner_info' : owner_info,
            'owner_ans_us' : owner_ans_us,
            'owner_ans_self' : owner_ans_self,
            'all_answers' : all_answers_paginated,
            'is_owner' : is_owner,
            'list__us_saved_by_user' : list__us_saved_by_user,
            'list__self_saved_by_user' : list__self_saved_by_user,
            'all_bookmarked' : all_bookmarked,
            'from_profile_page' : from_profile_page,
            'this_userinfoadditional' : this_userinfoadditional,
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/v2__profile.html', context)
    
    ## 타인 프로필
    else:
        is_owner = False

        ## 이 사람의 정답
        owner_ans_us = AnswersForFromUs.objects.filter(author_id=profile_owner, is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
        )
        owner_ans_self = AnswersForFromSelf.objects.filter(author_id=profile_owner, is_shared=True).order_by('-created_at_time').annotate(
            count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
        )
        
        ## 문제는, 서로 다른 모델의 queryset을 합쳐서(merge) 보여줘야 한다는 것.
        ## See : https://howchoo.com/django/combine-two-querysets-with-different-models
        ## 근데 아래 방법으로 하면 performance가 현저히 낮아진다고 함. 특히 queryset이 커짐에 따라.
        all_answers = sorted(
            chain(owner_ans_us, owner_ans_self),
            key=lambda post: post.created_at_time, reverse=True
        )

        if request.user.is_authenticated:
            ## 이 사람의 글 중 내가 Bookmark한 글
            us_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_saved_by_user = SavedAnswers.objects.filter(bookmarker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_saved_by_user = list(us_saved_by_user)
            list__self_saved_by_user = list(self_saved_by_user)

            ## 이 사람의 글 중 내가 Like한 글
            us_liked_by_user = Likes.objects.filter(liker=request.user, ans_type='us').values_list('ans_us_ref', flat=True)
            self_liked_by_user = Likes.objects.filter(liker=request.user, ans_type='self').values_list('ans_self_ref', flat=True)
            list__us_liked_by_user = list(us_liked_by_user)
            list__self_liked_by_user = list(self_liked_by_user)

            pre_context = {
                'owner_info' : profile_owner.userinfo, 
                'owner_ans_us' : owner_ans_us,
                'owner_ans_self' : owner_ans_self,
                'list__us_saved_by_user' : list__us_saved_by_user,
                'list__self_saved_by_user' : list__self_saved_by_user,
                'list__us_liked_by_user' : list__us_liked_by_user,
                'list__self_liked_by_user' : list__self_liked_by_user,
                'is_owner' : is_owner,
                'from_profile_page' : from_profile_page,
                'this_userinfoadditional' : this_userinfoadditional,
                'all_answers' : all_answers,
            }
        else:
            pre_context = {
                'owner_info' : profile_owner.userinfo, 
                'owner_ans_us' : owner_ans_us,
                'owner_ans_self' : owner_ans_self,
                'is_owner' : is_owner,
                'from_profile_page' : from_profile_page,
                'this_userinfoadditional' : this_userinfoadditional,
                'all_answers' : all_answers,
            } 
        
        context = {**pre_context, **navbar_context}
        return render(request, 'main/v2__profile.html', context)

def about(request):
    navbar_context = navbar(request)

    pre_context = {

    }

    context = {**navbar_context, **pre_context}
    return render(request, 'main/about.html', context)

def this_question(request, ques_id):
    navbar_context = navbar(request)

    ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=ques_id, is_shared=True).order_by('-created_at_time')
    this_question = QuestionsFromUs.objects.get(id=ques_id)

    ## 답변 있는지 여부 먼저 체크해야됨.
    if ans_for_this_ques:
        exists = True
    else:
        exists = False
    
    pre_context = {
        'exists' : exists,
        'ans_for_this_ques' : ans_for_this_ques,
        'this_question' : this_question,
    }

    context = {**pre_context, **navbar_context}
    return render(request, 'main/this_question.html', context)

##### 오늘 뮤지엄이 던지는 질문 #####
def d_____create_ans_us_short(request):
    now = timezone.now()
    string__today = str(now).split()[0]
    today = datetime.strptime(string__today, '%Y-%m-%d').date()
    
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
                form = AnswersForFromUsForm(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save(commit=False)
                    # 이미지 유무 체크
                    if form.cleaned_data.get('image'):
                        pass
                    else:
                        random_image = RandomImages.objects.get(id=randImg())
                        instance.image = random_image.image

                    instance.author_id = request.user
                    instance.question_id = today_ques
                    # instance.created_at = str(today)
                    

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
                    form = AnswersForFromUsForm(request.POST, request.FILES)
                    if form.is_valid():
                        instance = form.save(commit=False)
                        # 이미지 유무 체크
                        if form.cleaned_data.get('image'):
                            pass
                        else:
                            random_image = RandomImages.objects.get(id=randImg())
                            instance.image = random_image.image
                        instance.author_id = request.user
                        instance.question_id = today_ques
                        # instance.created_at = str(today)

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

def create_ans_us(request):
    now = timezone.now()
    string__today = str(now).split()[0]
    today = datetime.strptime(string__today, '%Y-%m-%d').date()
    
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
                form = AnswersForFromUsForm(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save(commit=False)
                    # 이미지 유무 체크
                    if form.cleaned_data.get('image'):
                        pass
                    else:
                        random_image = RandomImages.objects.get(id=randImg())
                        instance.image = random_image.image

                    instance.author_id = request.user
                    instance.question_id = today_ques
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
                    form = AnswersForFromUsForm(request.POST, request.FILES)
                    if form.is_valid():
                        instance = form.save(commit=False)
                        # 이미지 유무 체크
                        if form.cleaned_data.get('image'):
                            pass
                        else:
                            random_image = RandomImages.objects.get(id=randImg())
                            instance.image = random_image.image
                        instance.author_id = request.user
                        instance.question_id = today_ques
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

def create_ans_us_for_today(request):
    now = timezone.now()
    string__today = str(now).split()[0]
    today = datetime.strptime(string__today, '%Y-%m-%d').date()
    
    navbar_context = navbar(request)

    ## 로그인되어있는 경우와 아닌 경우 구분해야 함. 첫번째 질문에 한하여, 로그인 안되어 있어도 일단 답변은 가능. 하지만 곧바로 가입/로그인 유도해야 한다.
    if request.user.is_authenticated == False:
        today_ques = QuestionsFromUs.objects.get(question_no=1)
        is_member = 'False'
        mode = 'create'

        pre_context = {
            'today_ques' : today_ques,
            'is_member' : is_member,
            'mode' : mode,
        }

        context = {**navbar_context, **pre_context}
        return render(request, 'main/C_ans_us.html', context)

    ## 로그인 되어 있는 경우
    elif request.user.is_authenticated:
        this_user = request.user
        is_member = "True"
        mode = 'create'

        ## 북마크된 답변들 가져오기
        us_saved_by_user = SavedAnswers.objects.filter(bookmarker=this_user, ans_type='us').values_list('ans_us_ref', flat=True)
        list__us_saved_by_user = list(us_saved_by_user)
        self_saved_by_user = SavedAnswers.objects.filter(bookmarker=this_user, ans_type='us').values_list('ans_self_ref', flat=True)
        list__self_saved_by_user = list(self_saved_by_user)

        form = AnswersForFromUsForm(request.POST)
        ## 이 유저가 답변을 생성한 적이 없는 경우 (initial) => empty queryset
        if not AnswersForFromUs.objects.filter(author_id=request.user):            
            ## 첫번째 질문 가져오기
            today_ques = QuestionsFromUs.objects.get(question_no=1)
            today_ques_id = today_ques.id

            ## 이 질문에 대한 답변들
            all_ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=today_ques_id, is_shared=True).order_by('-created_at_time')
            
            ## 답변 제출
            if request.method == 'POST':
                form = AnswersForFromUsForm(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save(commit=False)
                    # 이미지 유무 체크
                    if form.cleaned_data.get('image'):
                        pass
                    else:
                        random_image = RandomImages.objects.get(id=randImg())
                        instance.image = random_image.image

                    instance.author_id = request.user
                    instance.question_id = today_ques
                    instance.from_today = True

                    instance.save()
                    return redirect('/')
        
        ## 첫번째 질문에 답을 한 경우 (두번째 이후인 경우)
        else:
            ## 가장 최근 질문의 가장 최근 답변일 가져오기
            # 1) 이 유저가 '오늘의 질문 받기'를 통해 답변한 답변들 모두 가져오기
            # answers_created_from_today = AnswersForFromUs.objects.filter(author_id=request.user, from_today_ques=True).values('question_id').order_by('-question_id')
            answers_created_from_today = AnswersForFromUs.objects.filter(author_id=request.user, from_today_ques=True).order_by('-question_id')
            list__all_ques_from_today = list(answers_created_from_today) # 딕셔너리가 들어있는 리스트
            
            # question_id 중 최댓값, 즉 list__all_ques_from_today의 0번째 인덱스 가져오기
            latest_ques_id = list__all_ques_from_today[0].question_id.id
            # 이 질문의 created_at 가져오기
            latest_created_at = list__all_ques_from_today[0].created_at
            # 가장 최근 질문의 가장 최근 답변일이 가져와졌다. 이 날짜와 today의 값이 서로 같은지 다른지 확인해줘야 한다.
            if latest_created_at < today:
                # 다음 질문 가져오기
                latest_ques = QuestionsFromUs.objects.get(id=latest_ques_id)
                today_ques_no = latest_ques.question_no + 1
                today_ques = QuestionsFromUs.objects.get(question_no=today_ques_no)

                ## 이 질문에 대한 answer가 있는지 확인
                while True:
                    if AnswersForFromUs.objects.filter(author_id=request.user, question_id=today_ques.id): # 이미 존재
                        today_ques_no = today_ques_no+1
                        today_ques = QuestionsFromUs.objects.get(question_no=today_ques_no)
                    else: # 그대로 진행
                        break

                ## 이 질문에 대한 답변들
                all_ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=today_ques.id, is_shared=True).order_by('-created_at_time')

                if request.method == "POST":
                    form = AnswersForFromUsForm(request.POST, request.FILES)
                    if form.is_valid():
                        instance = form.save(commit=False)
                        # 이미지 유무 체크
                        if form.cleaned_data.get('image'):
                            pass
                        else:
                            random_image = RandomImages.objects.get(id=randImg())
                            instance.image = random_image.image
                        instance.author_id = request.user
                        instance.question_id = today_ques
                        instance.from_today = True
                        instance.save()

                        return redirect('/')

            ## 아직 날짜가 지나지 않았을 때 (수정만 가능함)
            elif latest_created_at == today:
                ## 오늘의 질문은 latest_ques와 같음
                latest_ques = QuestionsFromUs.objects.get(id=latest_ques_id)
                today_ques_no = latest_ques.question_no
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

def create_ans_us_not_for_today(request, ques_id):
    now = timezone.now()
    string__today = str(now).split()[0]
    today = datetime.strptime(string__today, '%Y-%m-%d').date()
    
    navbar_context = navbar(request)

    this_ques = QuestionsFromUs.objects.get(id=ques_id)
    ## 이 질문에 대한 답변들
    all_ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=this_ques, is_shared=True).order_by('-created_at_time')
    
    ## 로그인되어있는 경우와 아닌 경우 구분해야 함. 첫번째 질문에 한하여, 로그인 안되어 있어도 일단 답변은 가능. 하지만 곧바로 가입/로그인 유도해야 한다.
    if request.user.is_authenticated == False:
        is_member = 'False'
        mode = 'create'

        pre_context = {
            'this_ques' : this_ques,
            'is_member' : is_member,
            'mode' : mode,
        }

        context = {**navbar_context, **pre_context}
        return render(request, 'main/C_ans_us_not_today.html', context)

    ## 로그인 되어 있는 경우
    elif request.user.is_authenticated:
        this_user = request.user
        is_member = "True"
        mode = 'create'

        ## 북마크된 답변들 가져오기
        us_saved_by_user = SavedAnswers.objects.filter(bookmarker=this_user, ans_type='us').values_list('ans_us_ref', flat=True)
        list__us_saved_by_user = list(us_saved_by_user)
        self_saved_by_user = SavedAnswers.objects.filter(bookmarker=this_user, ans_type='us').values_list('ans_self_ref', flat=True)
        list__self_saved_by_user = list(self_saved_by_user)

        form = AnswersForFromUsForm(request.POST)
        
        if AnswersForFromUs.objects.filter(author_id=request.user, question_id=this_ques): # 이 질문에 대한 답변이 있음
            all_ans_for_this_ques = AnswersForFromUs.objects.filter(question_id=this_ques.id, is_shared=True).order_by('-created_at_time')
            my_ans_for_this_ques = AnswersForFromUs.objects.get(question_id=this_ques.id, author_id=this_user)
            message = "이 질문에 이미 답을 했어요."
            answerable = False
                    
            pre_context = {
                'this_ques' : this_ques,
                'all_ans_for_this_ques' : all_ans_for_this_ques,
                'my_ans_for_this_ques' : my_ans_for_this_ques,
                'message' : message,
                'answerable' : answerable,
                'list__us_saved_by_user' : list__us_saved_by_user,
                'list__self_saved_by_user' : list__self_saved_by_user,
                'mode' : mode
            }

            context = {**pre_context, **navbar_context}
            return render(request, 'main/C_ans_us_not_today.html', context)
        
        else:
            answerable = True
        ## 답변 제출
            if request.method == 'POST':
                form = AnswersForFromUsForm(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save(commit=False)
                    # 이미지 유무 체크
                    if form.cleaned_data.get('image'):
                        pass
                    else:
                        random_image = RandomImages.objects.get(id=randImg())
                        instance.image = random_image.image

                    instance.author_id = request.user
                    instance.question_id = QuestionsFromUs.objects.get(id=ques_id) 
                    instance.from_today = False
                    instance.save()
                    return redirect('/')
    
        pre_context = {
            'form' : form,
            'this_ques' : this_ques,
            'this_user' : this_user,
            'all_ans_for_this_ques' : all_ans_for_this_ques,
            'is_member' : is_member,
            'list__us_saved_by_user' : list__us_saved_by_user,
            'list__self_saved_by_user' : list__self_saved_by_user,
            'mode' : mode
        }

        context = {**pre_context, **navbar_context}
        return render(request, 'main/C_ans_us_not_today.html', context)


def detail_ans_us(request, ans_us_id):
    navbar_context = navbar(request)

    this_ans = AnswersForFromUs.objects.get(id=ans_us_id)
    this_ans_ques_no = this_ans.question_id.question_no
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
        if request.user:
            current_user = UserInfo.objects.get(this_user=request.user)
        else:
            current_user = ''

    else:
        editable = ''
        bookmarked = ''
        current_user = ''

    ## 다른 [오리지널스가 던지는 질문]들 보기
    this_question_id = QuestionsFromUs.objects.filter(question_no=this_ans_ques_no).values_list('id', flat=True)
    all_ans_us = AnswersForFromUs.objects.filter(is_shared=True, question_id=this_question_id[0]).exclude(id=ans_us_id).order_by('-created_at_time').annotate(
        count_comments = Count('commentansus') ## annotate은 댓글 갯수 가져오는 용도.
    )

    ## 댓글
    comments = CommentAnsUs.objects.filter(ans=ans_us_id).order_by('created_at_time')

    pre_context = {
        'this_ans' : this_ans,
        'editable' : editable,
        'bookmarked' : bookmarked,
        'all_ans_us' : all_ans_us,
        'comments' : comments,
        'ans_us_id' : ans_us_id,
        'current_user' : current_user,
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
            ans_instance = ans_form.save(commit=False)
            # 이미지 유무 체크
            '''
            지금까지 아래처럼 하고 있었음. 그래서 이미지 수정해도 변경이 반영되지 않음.
            # if ans_form.cleaned_data.get('image'):
            #     pass
            # else:
            #     random_image = RandomImages.objects.get(id=randImg())
            #     ans_instance.image = random_image.image
            '''
            if ans_instance.image:
                ans_to_update.image = ans_instance.image
            else:
                pass

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

@login_required(login_url="/login")
def delete_ans_us(request, ans_us_id):
    this_ans = AnswersForFromUs.objects.get(id = ans_us_id)

    if User.objects.get(id=request.user.id) == this_ans.author_id:
        this_ans.delete()
    else:
        pass

    return redirect('/')

##### 내가 나에게 던지는 질문 #####
def d_____create_ans_self(request):
    navbar_context = navbar(request)

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

def create_ans_self(request):
    navbar_context = navbar(request)

    ques_form = QuestionsFromSelfForm(request.POST, request.FILES)
    ans_form = AnswersForFromSelfForm(request.POST)
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST': 
            ## Question 먼저 validate
            if ques_form.is_valid():
                ques_instance = ques_form.save(commit=False)
                ## 이미지 유무 체크
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
        return render(request, 'main/v2__C_ans_self.html', context)
    
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
        if request.user:
            current_user = UserInfo.objects.get(this_user=request.user)
        else:
            current_user = ''
    else: 
        editable = ''
        bookmarked = ''
        current_user = ''

    ## 다른 [나에게 던지는 질문]들 노출
    all_ans_self = AnswersForFromSelf.objects.filter(is_shared=True).exclude(id=ans_self_id).order_by('-created_at_time').annotate(
        count_comments = Count('commentansself') ## annotate은 댓글 갯수 가져오는 용도.
    )

    ## 댓글
    comments = CommentAnsSelf.objects.filter(ans=ans_self_id).order_by('created_at_time')

    pre_context = {
        'this_ans' : this_ans,
        'editable' : editable,
        'bookmarked' : bookmarked,
        'all_ans_self' : all_ans_self,
        'comments' : comments,
        'ans_self_id' : ans_self_id,
        'current_user' : current_user,
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

@login_required(login_url="/login")
def delete_ans_self(request, ans_self_id):
    this_ans = AnswersForFromSelf.objects.get(id = ans_self_id)
    this_ques = QuestionsFromSelf.objects.get(id=this_ans.question_id.id)
    
    if User.objects.get(id=request.user.id) == this_ans.author_id:
        this_ques.delete()
    else:
        pass
    return redirect('/')

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

##### Like 기능 #####
def likes(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        ans_type = data['ans_type']
        ans_us_ref = data['ans_us_ref']
        ans_self_ref = data['ans_self_ref']
        if request.method == 'POST':
            form = LikesForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                ## 현재 like한 놈이 이미 DB에 존재할 때는 삭제
                if ans_self_ref == '' and Likes.objects.filter(ans_type=ans_type, ans_us_ref=ans_us_ref, liker=request.user).exists(): ## Somehow, .get()을 쓰면 exists()가 안된다.
                    print('해당 오던질은 이미 like했습니다. like를 취소합니다.')
                    Likes.objects.get(ans_type=ans_type, ans_us_ref=ans_us_ref, liker=request.user).delete()

                    ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                    return redirect('/me')
                elif ans_us_ref == '' and Likes.objects.filter(ans_type=ans_type, ans_self_ref=ans_self_ref, liker=request.user).exists(): ## Somehow, .get()을 쓰면 exists()가 안된다.
                    print('해당 나던질은 이미 like했습니다. like를 취소합니다.')
                    Likes.objects.get(ans_type=ans_type, ans_self_ref=ans_self_ref, liker=request.user).delete()

                    ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                    return redirect('/me')

                ## 그렇지 않은 경우에는 저장
                else:
                    instance.ans_type = ans_type
                    if ans_type == 'us':
                        instance.ans_us_ref = AnswersForFromUs.objects.get(id=ans_us_ref) 
                    elif ans_type == 'self':
                        instance.ans_self_ref = AnswersForFromSelf.objects.get(id=ans_self_ref) 
                    instance.liker = request.user
            
                    instance.save()
                    print(instance.ans_type, instance.ans_self_ref, instance.ans_us_ref, instance.liker)
                    
                    ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                    return redirect('/me')
            else:
                print('@@@@@@ Validation failed due to : ', form.errors)
    else:
        pass

##### 중요한 질문 기능 #####
def author_favorite(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        ans_us = data['ans_us']
        ans_self = data['ans_self']

        if ans_us == '':
            this_ans = AnswersForFromSelf.objects.get(id=ans_self)
        elif ans_self == '':
            this_ans = AnswersForFromUs.objects.get(id=ans_us)
        
        if this_ans.author_favorite == True:
            this_ans.author_favorite = False
            this_ans.save()
        elif this_ans.author_favorite == False:
            this_ans.author_favorite = True
            this_ans.save()
        
        ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
        return redirect('/me')
        
    else:
        pass

##### 가입되지 않는 경우 (seldom) #####
def csrf_failure(request, reason=""):
    context = {
        'message' : 'sorry'
    }
    return render(request, 'main/csrf_failure.html', context)

##### Comment #####
def del_comment_ans_us(request):
    data = json.loads(request.body)
    comment_to_delete = data['thisComment']
    
    this_comment = CommentAnsUs.objects.get(pk=comment_to_delete)
    if this_comment.author.this_user == request.user:
        if request.method == 'DELETE':
            delete_instance = this_comment
            delete_instance.delete()
            return redirect('/me')
    else:
        print("CANNOT DELETE SOMEONE ELSE'S COMMENT")
        return redirect('/me')

def create_comment_ans_us(request):
    print('댓글 작성 호출됨 ANS-US')
    if request.user.is_authenticated:
        data = json.loads(request.body)
        ans = data['ans']
        body = data['body']

        if request.method == 'POST':
            form = CommentAnsUsForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.ans = AnswersForFromUs.objects.get(pk=ans)
                instance.body = body
                instance.author = UserInfo.objects.get(this_user = request.user)
            
                instance.save()
                print("댓글 작성 완료!")
                    
                ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                return redirect('/me')
            else:
                print('@@@@@@ Validation failed due to : ', form.errors)
    else:
        pass

def del_comment_ans_self(request):
    data = json.loads(request.body)
    comment_to_delete = data['thisComment']
    
    this_comment = CommentAnsSelf.objects.get(pk=comment_to_delete)
    if this_comment.author.this_user == request.user:
        if request.method == 'DELETE':
            delete_instance = this_comment
            delete_instance.delete()
            return redirect('/me')
    else:
        print("CANNOT DELETE SOMEONE ELSE'S COMMENT")
        return redirect('/me')

def create_comment_ans_self(request):
    print('댓글 작성 호출됨 ANS-SELF')
    if request.user.is_authenticated:
        data = json.loads(request.body)
        ans = data['ans']
        body = data['body']

        if request.method == 'POST':
            form = CommentAnsSelfForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.ans = AnswersForFromSelf.objects.get(pk=ans)
                instance.body = body
                instance.author = UserInfo.objects.get(this_user = request.user)
            
                instance.save()
                print("댓글 작성 완료!")
                    
                ## 아래 return 부분 잘 이해 안됨. return만 쓰면 에러 뜬다. 그렇다고 아래처럼 쓰면 아무런 반응 없음.
                return redirect('/me')
            else:
                print('@@@@@@ Validation failed due to : ', form.errors)
    else:
        pass

##### 검색 기능 #####
class SearchFormView(FormView):
    form_class = SearchForm
    template_name = 'main/search_result.html'

    def form_valid(self, form):
        keyword = form.cleaned_data['search_keyword']
        ans_us_list = AnswersForFromUs.objects.filter(Q(body__icontains=keyword)).distinct()
        ans_self_list = AnswersForFromSelf.objects.filter(Q(body__icontains=keyword)).distinct()

        context = {
            'search_form' : form,
            'keyword' : keyword,
            'search_result' : ans_us_list,
            'search_result_2' : ans_self_list,
        }
        # if which == 'answers':    
        #     keyword = form.cleaned_data['search_keyword']
        #     ans_us_list = AnswersForFromUs.objects.filter(Q(body__icontains=keyword)).distinct()
        #     ans_self_list = AnswersForFromSelf.objects.filter(Q(body__icontains=keyword)).distinct()

        #     context = {
        #         'search_form' : form,
        #         'keyword' : keyword,
        #         'search_result' : ans_us_list,
        #         'search_result_2' : ans_self_list,
        #     }

        # elif which == 'questions' :
        #     keyword = form.cleaned_data['search_word']
        #     us_ques_list = QuestionsFromUs.objects.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword) | Q(content__icontains=keyword)).distinct()
        #     self_ques_list = QuestionsFromSelf.objects.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword) | Q(content__icontains=keyword)).distinct()

        #     context = {
        #         'search_form' : form,
        #         'keyword' : keyword,
        #         'search_result' : us_ques_list,
        #         'search_result_2' : self_ques_list,
        #     }

        # elif which == 'users':
        #     keyword = form.cleaned_data['search_word']
        #     user_list = UserInfo.objects.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword) | Q(content__icontains=keyword)).distinct()

        #     context = {
        #         'search_form' : form,
        #         'keyword' : keyword,
        #         'search_result' : user_list,
        #     }

        return render(self.request, self.template_name, context)

##### 공지사항 #####
def notice(request):
    all_notice = Notice.objects.all().order_by('-created_at')
    
    context = {
        'all_notice' : all_notice,
    }

    return render(request, 'main/notice.html', context)