from common.forms import UserForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User

import sys
sys.path.append('..')
from test_rec.models import TmpUser


# request의 유저가 정상적으로 테스트를 마쳤는지 확인하는 함수
def check_SessionStorageInfo(request):
    mbti = request.session.get('MBTI', None)
    ennear_ans = request.session.get('ennear_ans', None)
    ennear_res = request.session.get('ennear_res', None)
    prefer_movie_id = request.session.get('prefer_movie_id', None)
    recommended_character_id = request.session.get('recommended_character_id', None)
    if mbti == None:
        print('MBTI is None')
        return False
    if ennear_ans == None:
        return False
    else: print(len(request.session['ennear_ans']))
    if ennear_ans == None:
        return False
    if prefer_movie_id == None:
        return False
    if recommended_character_id == None:
        return False
    return True


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form':form})


# Create your views here.
def index(request):
    if request.user.is_authenticated:  #로그인이 되어있는지 확인
        print('로그인 OK')
        if check_SessionStorageInfo(request): #테스트를 마쳤는지, TmpUser객체를 생성해야하는지 확인
            print('세션스토리지 OK')
            # TmpUser 객체 생성 후 세션스토리지 내용 저장
            tmpuser = TmpUser.objects.create(create_time=timezone.now()) #TmpUser 객체 생성
            tmpuser.MBTI = request.session['MBTI']
            tmpuser.ennear_ans = request.session['ennear_ans']
            tmpuser.ennear_res = request.session['ennear_res']
            tmpuser.prefer_movie_id = request.session['prefer_movie_id']
            tmpuser.recommended_character_id = request.session['recommended_character_id']
            tmpuser.save()

            user = request.user        #로그인한 유저의 정보를 가져옴
            tmpuser.LoginUser = user   #로그인한 유저의 정보를 TmpUser 객체에 저장 -> 로그인유저와 tmp유저 연결됨
            tmpuser.save()

    context = {
        'my_person_list': [],
        'datetime' : ""
    }
    return render(request, 'index.html', context)


@login_required(login_url='common:login')
def user_test_history(request):
    user = request.user
    tmpusers = TmpUser.objects.filter(LoginUser=user)
    context = {
        'tmpusers' : tmpusers
    }
    return render(request, 'common/user_test_history.html', context)