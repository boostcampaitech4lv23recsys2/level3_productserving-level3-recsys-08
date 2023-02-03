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
character_df = pd.read_pickle(pickle_path / '230130_Popular_movie_character_2867_cwj.pickle')


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
        'characters' : [
                        "https://static1.personality-database.com/profile_images/10372ac29c714ea8aa84fdfccfd9ae8e.png",\
                        "https://static1.personality-database.com/profile_images/fc179ba7fe644eaa82a1aca584e16868.png",\
                        "https://static1.personality-database.com/profile_images/ec0fdef9370245c69e9547daf3eff906.png",\
                        "https://static1.personality-database.com/profile_images/1d86aef46ec14549b24000306bc36db9.png",\
                        "https://static1.personality-database.com/profile_images/3bcb54ca72024d8a9c00dae8712009f0.png",\
                        "https://static1.personality-database.com/profile_images/f614546e3d5e434c98b695fe7735a98a.png",\
                        "https://static1.personality-database.com/profile_images/3877aed32c3b4d7185b22eabd80b9939.png",\
                        "https://static1.personality-database.com/profile_images/c207665f45f14fb2b9ccc78554e68790.png",\
                        "https://static1.personality-database.com/profile_images/be417e9fdf2e4604a564d6ceaa1b6b28.png",\
                        "https://static1.personality-database.com/profile_images/0087da2072a14eec8d01e541e9d9e98f.png",\
                        ]
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
    if len(tmpusers) == 0:
        return redirect('index')
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
    character_images = [character_df[character_df['CharacterId']==int(id)]['img_src'].values[0] \
                        for id in recommended_character_ids \
                        if len(character_df[character_df['CharacterId']==int(id)]['img_src']) > 0 ]
    character_id = [character_df[character_df['CharacterId']==int(id)]['CharacterId'].values[0] \
                    for id in recommended_character_ids \
                    if len(character_df[character_df['CharacterId']==int(id)]['CharacterId']) > 0 ]
    zip_character_info = zip(character_images, character_id)
    # 템플릿에 넘겨줄 context
    context = {
        'user' : User,
        'user_name' : user.username,
        'mbti': mbti,
        'prefer_movie_posters' : prefer_movie_posters,
        # 'character_images' : character_images,
        # 'character_id' : character_id,
        'zip_character_info' : zip_character_info,
        'tmpusers' : list(tmpusers)[-min(5, len(tmpusers)):][::-1],
    }
    return render(request, 'common/user_profile.html', context)

@login_required(login_url='common:login')
def delete_tmpuser(request, tmpuser_id):
    tmpuser = TmpUser.objects.get(id=tmpuser_id)
    tmpuser.delete()
    return redirect('common:user_profile')

# MBTI 상세 페이지 함수
def show_mbti_info(request, mbti):
    get_mbti = mbti
    
    context = {
        'mbti' : [get_mbti]
    }
    return render(request, 'common/mbti_info.html', context)