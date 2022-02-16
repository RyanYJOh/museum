from random import paretovariate
from django.shortcuts import render, redirect
from .forms import RegisterForm
from main.forms import AnswersForFromUsForm
from main.models import AnswersForFromUs, RandomImages, QuestionsFromUs, User
from main.views import randImg
from django.contrib.auth import login, authenticate, logout
import json
import random
# from django.contrib.auth.views import LoginView

def register(request):
    if request.method == 'POST':
        '''
        posted = request.POST.copy()
        posted['username'] = request.POST['email'].split('@')[0]
        request.POST = posted
        form = RegisterForm(posted)
        '''
        form = RegisterForm(request.POST)
        if form.is_valid:
            form.save()
            '''
            instance = form.save(commit=False)
            email_slug = instance.email.split('@')[0]
            ## username에 넣기 전에 중복체크.
            if User.objects.filter(username=instance.username).exists():
                instance.username = email_slug+str(random.randrange(1, 1000))
            else: 
                instance.username=email_slug
            
            instance.save()
            '''

            ## 자동 로그인
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            newUser = authenticate(request, username=username, password=password)
            if newUser:
                login(request, newUser)
                return redirect('/member/userinfo')
            else:
                return redirect('/join')
        else:
            print('THE FORM IS INVALID')
    else:
        form = RegisterForm()

    context = {
        'form' : form,
    }
    return render(request, 'register/register.html', context) 

##### 비회원 답변 저장 #####
def nonMemberAnswer(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        form = AnswersForFromUsForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.body = data['body']
            random_image = RandomImages.objects.get(id=randImg())
            instance.image = random_image.image
            instance.is_shared = data['is_shared']
            instance.question_id = data['question_no']
            instance.author_id = request.user
            instance.created_at = data['created_at']
            instance.updated_at = instance.created_at

            instance.save()
    
            return redirect('/')
        else:
            print("Validation 실패!!!!!!!!!!!!!!!!! due to :", form.errors)

from django.core.mail.message import EmailMessage

def send_email(request):
    subject = "message"
    to = ["yyjo1104@naver.com"]
    from_email = "this.is.originals.official@gmail.com"
    message = "메지시 테스트"
    EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send()