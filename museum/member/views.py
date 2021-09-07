from django.shortcuts import render, redirect, HttpResponseRedirect
from .forms import UserInfoForm
from django.contrib.auth.models import User
from .models import UserInfo
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from django.contrib.auth import login, authenticate

## 가입 및 자동 로그인 후 사용자 정보 입력 화면
@login_required(login_url="/login")
def create_userinfo(request):
    if request.method == 'POST':
        form = UserInfoForm(request.POST, request.FILES)
        if form.is_valid:
            instance = form.save(commit=False)
            instance.this_user = request.user ## this_user에 현재 로그인된 유저 저장
            
            this_email = request.user.email
            email_splitted = this_email.split('@')[0]
            instance.slug = str(email_splitted) ## response.email 되나 이거?
            form.save()
        return HttpResponseRedirect('/')
    else:
        form = UserInfoForm()
    
    message1 = "환영합니다!"
    # message2 = "이름과 사진을"
    context = {
        'form' : form,
        'message1' : message1
    }
    return render(request, 'member/userinfo.html', context)

## 사용자 정보 수정 화면
@login_required(login_url="/login")
def update_userinfo(request, username):
    user_to_update = User.objects.get(username = username)
    userinfo_to_update = UserInfo.objects.get(this_user = user_to_update)
    if request.method == 'POST':
        form = UserInfoForm(request.POST, request.FILES)
        if form.is_valid:
            instance = form.save(commit=False)
            userinfo_to_update.slug = instance.slug
            userinfo_to_update.real_name = instance.real_name
            userinfo_to_update.self_intro = instance.self_intro
            userinfo_to_update.persona_type = instance.persona_type
            print(request.FILES)
            ## 프사 선택한 경우
            if request.FILES.get('profile_image'):
                userinfo_to_update.profile_image = instance.profile_image
            ## 이미지 필드에 아무런 변경도 하지 않고 제출한 경우
            else :
                userinfo_to_update.profile_image = userinfo_to_update.profile_image

            userinfo_to_update.save()

        return HttpResponseRedirect('/profile/{}'.format(request.user.username))

    ## 수정하기 위해 페이지 진입
    else:
        form = UserInfoForm(instance=userinfo_to_update)
        update_mode = 'True'
        # form.fields['real_name'].widget.attrs['readonly'] = True ## 이름은 수정 불가
        message = "내 정보 수정"
        context = {
            'form' : form,
            'message' : message,
            'update_mode' : update_mode,
        }
        return render(request, 'member/userinfo.html', context)

## '내 프로필' 화면
@login_required(login_url="/login")
def my_profile(request):
    ## 로그인만 되어 있다면 half-valid member
    if request.user.is_authenticated: 
        half_valid_member = request.user

        ## 로그인되어 있고, userinfo도 입력했다면 valid member
        if UserInfoForm.objects.filter(this_user=half_valid_member.id).exists(): 
            valid_member = UserInfo.objects.get(this_user = half_valid_member.id)

            context = {
                'this_member' : valid_member
            }
            ## 프로필 링크로 가려면 /{email_splitted} 들어와야함. 포맷팅 필요
            return render(request, 'member/userinfo.html', context)

        ## 로그인은 되어있는데, userinfo는 입력하지 않았다면 half-valid member
        else:
            return redirect('member/userinfo')
    
    ## 로그인되어 있지 않을 때
    else:
        return redirect('/join')

            

