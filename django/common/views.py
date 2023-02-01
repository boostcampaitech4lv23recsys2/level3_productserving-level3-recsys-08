from common.forms import UserForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import pickle
import pandas as pd
from pathlib import Path
import sys
sys.path.append('../test_rec')
from test_rec.models import TmpUser

# request의 유저가 정상적으로 테스트를 마쳤는지 확인하는 함수
def check_TmpUserInfo(request):
    try:
        user = TmpUser.objects.get(id=request.session['user_id'])
    except:
        return False
    if user == None:
        return False
    if user.MBTI == None:
        return False
    if user.ennea_ans1 == None:
        return False
    if user.ennea_ans2 == None:
        return False    
    if user.ennea_res == None:
        return False
    if user.prefer_movie_id == None:
        return False
    if user.recommended_character_id == None:
        return False
    return True


pickle_path = Path(__file__).parent.parent.parent.absolute()/"Utils/Pickle"
movieId2poster_path = pickle_path / 'movieid_to_poster_file.pickle'
mbti_df = pd.read_pickle(pickle_path / 'MBTI_merge_movieLens_3229_movie.pickle')


with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)



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
        if check_TmpUserInfo(request): #테스트를 마쳤는지 확인
            print('TmpUser 객체 OK')
            user = request.user        #로그인한 유저의 정보를 가져옴
            tmpuser = TmpUser.objects.get(id=request.session['user_id'])
            tmpuser.LoginUser = user   #로그인한 유저의 정보를 TmpUser 객체에 저장 -> 로그인유저와 tmp유저 연결됨
            tmpuser.save()

    context = {
        'my_person_list': [],
        'datetime' : "",
        'characters' : []
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


@login_required(login_url='common:login')
def user_profile(request):
    user = request.user
    tmpusers = TmpUser.objects.filter(LoginUser=user)
    mbti = tmpusers[len(tmpusers)-1].MBTI
    # prefer_movie_ids와 해당 포스터 파일이름 불러오는 과정
    tmp = [tmpuser.prefer_movie_id for tmpuser in tmpusers]
    prefer_movie_ids = [eval(tmp[i]) for i in range(len(tmp))]
    prefer_movie_ids = [item for sublist in prefer_movie_ids for item in sublist]
    prefer_movie_posters = [movieId_to_posterfile[int(id)] for id in prefer_movie_ids]
    # recommended_character_ids와 해당 이미지 파일 불러오는 과정
    tmp = [tmpuser.recommended_character_id for tmpuser in tmpusers]
    recommended_character_ids = [eval(tmp[i]) for i in range(len(tmp))]
    recommended_character_ids = [item for sublist in recommended_character_ids for item in sublist]
    character_images = [mbti_df[mbti_df['CharacterId']==int(id)]['img_src'].values[0] for id in recommended_character_ids]
    # 템플릿에 넘겨줄 context
    context = {
        'user' : user.username,
        'mbti': mbti,
        'prefer_movie_posters' : prefer_movie_posters,
        'character_images' : character_images,
        'tmpusers' : tmpusers,
    }
    return render(request, 'common/user_profile.html', context)