from common.forms import UserForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

import sys
sys.path.append('../test_rec')
from test_rec.models import TmpUser

# request의 유저가 정상적으로 테스트를 마쳤는지 확인하는 함수
def check_TmpUserInfo(request):
    try:
        user = TmpUser.objects.get(id=request.session['user_id'])
    except:
        return False
    if user.MBTI == None:
        return False
    if user.ennear_ans == None and len(user.ennear_res) != 10: #10인 이유: ["2", "B"] 문자열로 저장되어있음
        return False
    if user.ennear_res == None:
        return False
    if user.prefer_movie_id == None:
        return False
    if user.recommended_character_id == None:
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
    print("인덱스페이지입니당")
    try:
        print(f"index페이지 유저id:{request.session['user_id']}")
    except:
        pass
    if request.user.is_authenticated:
        print('로그인 OK')
        if check_TmpUserInfo(request):
            print('TmpUser 객체 OK')
            user = request.user
            tmpuser = TmpUser.objects.get(id=request.session['user_id'])
            tmpuser.LoginUser = user
            tmpuser.save()
            # print('User의 새로 추가된 테스트의 MBTI', user.tmpuser.last().MBTI)

    context = {
        'my_person_list': [],
        'datetime' : "",
        'characters' : ['ryuseungryong','wednesday']
    }
    return render(request, 'index.html', context)