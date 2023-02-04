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
    if user.fit_character_id == None:
        return False
    if user.recommended_character_sim == None:
        return False
    if user.fit_character_sim == None:
        return False
    return True


pickle_path = Path(__file__).parent.parent.parent.absolute()/"Utils/Pickle"

movie_df = pd.read_pickle(pickle_path / '230130_Popular_movie_1192_cwj.pickle')
character_df = pd.read_pickle(pickle_path / '230130_Popular_movie_character_2867_cwj.pickle')
cha_df_with_ko_title = pd.read_pickle(pickle_path / 'Popular_movie_character_2867_with_ko_title.pickle')

movieId2poster_path = pickle_path / 'movieid_to_poster_file.pickle'
with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)

characterid_to_hashtag_path = pickle_path / '230201_characterid_to_hashtag.pickle'
with open(characterid_to_hashtag_path, 'rb') as f:
    characterid_to_hashtag = pickle.load(f)


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

    # 인기있는 캐릭터 Top 10 CharacterId
    characterid = [18003, 19481, 7079, 9197, 8134, 5485, 6831, 4156, 1427, 8516]

    # 인기있는 캐릭터 Top 10의 정보를 담은 리스트
    cha_li1 = []
    for c in characterid:
        cha_li1.extend(cha_df_with_ko_title[cha_df_with_ko_title['CharacterId'] == c].to_dict(orient='records'))
        
    # 나와 성격이 같은 캐릭터 Top 10의 정보를 담은 리스트
    cha_li2 = []
    
    # 나와 궁합이 잘 맞는 캐릭터 Top 10의 정보를 담은 리스트
    cha_li3 = []
    
    context = {
        'my_person_list': [],
        'datetime' : "",
        'characters1' : cha_li1,
        'characters2' : cha_li2,
        'characters3' : cha_li3
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
    tmpusers = list(tmpusers)[::-1]
    print(tmpusers)
    if len(tmpusers) == 0:
        return redirect('index')
    mbti = tmpusers[len(tmpusers)-1].MBTI

    # prefer_movie_ids와 해당 영화정보 불러오는 과정
    tmp = [tmpuser.prefer_movie_id for tmpuser in tmpusers]
    prefer_movie_ids = [eval(tmp[i]) for i in range(len(tmp))]
    prefer_movie_ids = [item for sublist in prefer_movie_ids for item in sublist]
    movie_data = pd.DataFrame()
    for id in prefer_movie_ids:
        movie_data = movie_data.append(movie_df[movie_df['movieId']==int(id)])
    movie_data['poster'] = movie_data['movieId'].apply(lambda x: movieId_to_posterfile[x])
    movie_data = movie_data.to_dict(orient='records')

    # recommended_character_ids와 해당 캐릭터 정보 불러오는 과정
    tmp = [tmpuser.recommended_character_id for tmpuser in tmpusers]
    recommended_character_ids = [eval(tmp[i]) for i in range(len(tmp))]
    recommended_character_ids = [item for sublist in recommended_character_ids for item in sublist]
    character_data = pd.DataFrame()
    for id in recommended_character_ids:
        character_data = character_data.append(character_df[character_df['CharacterId']==int(id)])
    character_data = character_data.merge(movie_df[['ko_title', 'movieId']], on='movieId', how='left')
    character_data['CharacterId'] = character_data['CharacterId'].map(int)
    character_data = character_data.to_dict(orient='records')
    
    # 템플릿에 넘겨줄 context
    context = {
        'user' : User,
        'user_name' : user.username,
        'mbti': mbti,
        'character_data' : character_data,
        'movie_data' : movie_data,
        'tmpusers' : list(tmpusers)[: min(5, len(tmpusers))],
    }

    return render(request, 'common/user_profile.html', context)



def detail_tmpuser(request, tmpuser_id):
    tmpuser = TmpUser.objects.get(id=tmpuser_id)
    user = tmpuser.LoginUser
    mbti = tmpuser.MBTI

    prefer_movie_ids = tmpuser.prefer_movie_id
    movie_data = pd.DataFrame()
    for id in eval(prefer_movie_ids):
        movie_data = movie_data.append(movie_df[movie_df['movieId']==int(id)])
    movie_data['poster'] = movie_data['movieId'].apply(lambda x: movieId_to_posterfile[x])
    movie_data = movie_data.to_dict(orient='records')

    recommended_character_ids = tmpuser.recommended_character_id
    # data1은 나와 같은 MBTI를 가진 캐릭터 정보 담은 데이터 입니다.
    data1 = pd.DataFrame()
    for id in eval(recommended_character_ids):
        data1 = data1.append(character_df[character_df['CharacterId']==int(id)])
    data1 = data1.merge(movie_df[['movieId','ko_title','npop']], on='movieId', how='left')
    data1['CharacterId'] = data1['CharacterId'].map(int)
    data1['hashtag'] = data1.CharacterId.map(characterid_to_hashtag)
    
    data1['Enneagram_sim'] = eval(tmpuser.recommended_character_sim)
    cols=['CharacterId','Character','ko_title','MBTI','img_src','hashtag','npop','Enneagram_sim']
    data1 = data1[cols][:20].to_dict(orient='records')

    fit_character_ids = tmpuser.fit_character_id
    fit_character_data = pd.DataFrame()
    data2 = pd.DataFrame()
    for id in eval(fit_character_ids):
        data2 = data2.append(character_df[character_df['CharacterId']==int(id)])
    data2 = data2.merge(movie_df[['movieId','ko_title','npop']], on='movieId', how='left')
    data2['CharacterId'] = data2['CharacterId'].map(int)
    data2['hashtag'] = data2.CharacterId.map(characterid_to_hashtag)
    data2['Enneagram_sim'] = eval(tmpuser.fit_character_sim)
    cols=['CharacterId','Character','ko_title','MBTI','img_src','hashtag','npop','Enneagram_sim']
    data2 = data2[cols][:20].to_dict(orient='records')
    
    context = {
        'user' : user,
        'tmpuser' : tmpuser,
        'mbti': mbti,
        'data1': data1,
        'data2': data2,
        'movie_data' : movie_data,
    }
    return render(request, 'common/detail_tmpuser.html', context)


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