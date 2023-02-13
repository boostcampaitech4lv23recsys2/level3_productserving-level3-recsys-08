from common.forms import UserForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from .models import BatchTrain
from test_rec.models import TmpUser

from ast import literal_eval
import pickle
import pandas as pd
from pathlib import Path
import sys
sys.path.append('../test_rec')
from test_rec.models import TmpUser
sys.path.append('..')
from Utils import *

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

movie_df = pd.read_pickle(pickle_path / '230213_Popular_movie_1192_cwj.pickle')
character_df = pd.read_pickle(pickle_path / '230213_character_movie_merge.pickle')
character_info_df = pd.read_pickle(pickle_path / '230213_processed_ko_cha_info.pickle')
engram_sim = pd.read_pickle(pickle_path / 'enneagram_similarity_075_099.pickle')

movieId2poster_path = pickle_path / 'movieid_to_poster_file.pickle'
with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)

characterid_to_hashtag_path = pickle_path / '230203_characterid_to_hashtag.pickle'
with open(characterid_to_hashtag_path, 'rb') as f:
    characterid_to_hashtag = pickle.load(f)

mbti_ennea_df_path = pickle_path / 'MBTI_Enneagram_personality_tag.pickle'
with open(mbti_ennea_df_path, 'rb') as f:
    mbti_ennea_df = pickle.load(f)

fit_mbti_dict_path = pickle_path / '230201_fit_mbti_dict.pickle'
with open(fit_mbti_dict_path, 'rb') as f:
    fit_mbti_dict = pickle.load(f)


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
    test_count = TmpUser.objects.all().count()
    if request.user.is_authenticated:  #로그인이 되어있는지 확인
        print('로그인 OK')
        if check_TmpUserInfo(request): #테스트를 마쳤는지 확인
            print('TmpUser 객체 OK')
            user = request.user        #로그인한 유저의 정보를 가져옴
            tmpuser = TmpUser.objects.get(id=request.session['user_id'])
            tmpuser.LoginUser = user   #로그인한 유저의 정보를 TmpUser 객체에 저장 -> 로그인유저와 tmp유저 연결됨
            tmpuser.save()

    cha_li1 = []; cha_li2 = []; cha_li3 = []
    
    # 인기있는 캐릭터 Top 10 CharacterId
    characterid1 = [18003, 0, 7079, 9197, 8134, 5485, 6831, 4156, 1427, 8516]
    
    # 인기있는 캐릭터 Top 10의 정보를 담은 리스트
    for c in characterid1:
        cha_li1.extend(character_df[character_df['CharacterId'] == c].to_dict(orient='records'))
        # print(cha_li1)
        character_df[character_df.CharacterId.isin(characterid1)].to_dict(orient='records')
        char1 = character_df[character_df.CharacterId.isin(characterid1)]
        char1.sort_values('vote', ascending=False, inplace=True)
        char1_merge = char1.merge(character_info_df, on='CharacterId')
        cha_li1 = char1_merge.to_dict(orient='records')        

    if request.user.is_authenticated:
        user = request.user
        batch_recs = BatchTrain.objects.filter(Q(LoginUser_id=user) & Q(model_name="ADER")).order_by('-create_time')
        tmpusers = TmpUser.objects.filter(LoginUser=user).order_by('-create_time')
        # 테스트를 한 번이라도 한 유저
        if tmpusers:
            mbti = tmpusers[0].MBTI
            # ADER 추천이 있는 경우
            if batch_recs: 
                engram = tmpusers[0].ennea_res
                user_fit_MBTI = fit_mbti_dict[mbti]
                mbti_list=[mbti, user_fit_MBTI]

                batch_rec = batch_recs[0] # 배치 추천에서 최신 ADER 결과 가져오기
                rec_movie_list = literal_eval(batch_rec.recommended_movie_list)
                charcter_mbti_rec = mbti_filtering(mbti_list, character_df, rec_movie_list)
                character_rec_engram_sort = engram_sorting(engram, charcter_mbti_rec, engram_sim)
                result = character_rec_engram_sort.drop_duplicates(subset=['Character', 'Contents'])
                # 한글 이름, 설명 붙이기
                result = result.merge(character_info_df, on='CharacterId')
                ## 나와 같은 MBTI 추천 리스트 추출
                result_same = result[result.MBTI==mbti].copy()
                # npop, vote로 필터링
                result_same_npop = result_same.sort_values('npop',ascending=False)[:20]
                result_same_npop_vote = result_same.sort_values('vote',ascending=False)[:10]
                # 최신 영화 필터링
                result_same_latest = result_same[result_same.movieId>=300_000]
                # 합치고 중복 제거하기
                result_same_final = pd.concat([result_same_npop_vote,result_same_latest]).drop_duplicates(subset=['CharacterId'])
                # Enneagram 유사도로 정렬
                result_same_final.sort_values('Enneagram_sim',ascending=False,inplace=True)
                print(f"{result_same_final.shape = }")
                print(result_same_final[['CharacterId','name','ko_title','vote','npop','Enneagram_sim']])

                ## 나와 잘 맞는 MBTI 추천 리스트 추출
                result_fit = result[result.MBTI==user_fit_MBTI].copy()
                # npop, vote로 필터링
                result_fit_npop = result_fit.sort_values('npop',ascending=False)[:20]
                result_fit_npop_vote = result_fit.sort_values('vote',ascending=False)[:10]
                # 최신 영화 필터링
                result_fit_latest = result_fit[result_fit.movieId>=300_000]
                # 합치고 중복 제거하기
                result_fit_final = pd.concat([result_fit_npop_vote,result_fit_latest]).drop_duplicates(subset=['CharacterId'])
                # Enneagram 유사도로 정렬
                result_fit_final.sort_values('Enneagram_sim',ascending=False,inplace=True)
                print(f"{result_fit_final.shape = }")

                cha_li2 = result_same_final.to_dict(orient='records')
                cha_li3 = result_fit_final.to_dict(orient='records')
            # ADER 추천이 아직 없는 경우
            else:
                tmp = [tmpuser.recommended_character_id for tmpuser in tmpusers]
                characterid2 = [eval(str(tmp[i])) for i in range(len(tmp))]
                characterid2 = [item for sublist in characterid2 for item in sublist]  
                
                tmp = [tmpuser.fit_character_id for tmpuser in tmpusers]
                characterid3 = [eval(str(tmp[i])) for i in range(len(tmp))]
                try:
                    characterid3 = [item for sublist in characterid3 for item in sublist]  
                except: # None 값 예외처리
                    cha3 = []
                    for sublist in characterid3:
                        if sublist == None:
                            continue
                        for item in sublist:
                            cha3.extend(item)
                    characterid3 = cha3

                # 나와 성격이 같은 캐릭터 Top 10의 정보를 담은 리스트
                deduple_charcter_id2=[]
                for i in characterid2:
                    if i not in deduple_charcter_id2:
                        deduple_charcter_id2.append(i)
                deduple_charcter_id2_top10 = [int(i) for i in deduple_charcter_id2[:10]]
                char2 = character_df[character_df.CharacterId.isin(deduple_charcter_id2_top10)]
                char2_merge = char2.merge(character_info_df, on='CharacterId')
                cha_li2 = char2_merge.to_dict(orient='records')
                    
                # 나와 궁합이 잘 맞는 캐릭터 Top 10의 정보를 담은 리스트
                deduple_charcter_id3=[]
                for i in characterid3:
                    if i not in deduple_charcter_id3:
                        deduple_charcter_id3.append(i)
                deduple_charcter_id3_top10 = [int(i) for i in deduple_charcter_id3[:10]]
                char3 = character_df[character_df.CharacterId.isin(deduple_charcter_id3_top10)]
                char3_merge = char3.merge(character_info_df, on='CharacterId')
                cha_li3 = char3_merge.to_dict(orient='records')
        else:
            pass
    
    

    context = {
        'test_count': int(test_count)+1,
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
    tmpusers = TmpUser.objects.filter(LoginUser=user).order_by('-create_time')[:10]
    tmpusers = list(tmpusers)[::-1]
    if len(tmpusers) == 0:
        return redirect('index')
    mbti = tmpusers[0].MBTI    
    enneagram = tmpusers[0].ennea_res
    mbti_enneagram = mbti + ' ' + enneagram
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(mbti_enneagram)

    # 유저의 성격 태그
    user_tag = mbti_ennea_df[mbti_ennea_df['MBTI_Enneagram'] == mbti_enneagram]['tag']
    user_tag = " ".join(user_tag.values[0])

    # 유저의 성격 설명
    user_desc = mbti_ennea_df[mbti_ennea_df['MBTI_Enneagram'] == mbti_enneagram]['description'].values[0]

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
    character_data = character_data.merge(character_info_df, on='CharacterId', how='left')
    character_data['CharacterId'] = character_data['CharacterId'].map(int)
    character_data = character_data.to_dict(orient='records')

    tmp = [tmpuser.fit_character_id for tmpuser in tmpusers]
    fit_character_ids = [eval(tmp[i]) for i in range(len(tmp)) if tmp[i]]
    fit_character_ids = [item for sublist in fit_character_ids for item in sublist]
    fit_character_data = pd.DataFrame()
    for id in fit_character_ids:
        fit_character_data = fit_character_data.append(character_df[character_df['CharacterId']==int(id)])
    fit_character_data = fit_character_data.merge(character_info_df, on='CharacterId', how='left')
    fit_character_data['CharacterId'] = fit_character_data['CharacterId'].map(int)
    print(fit_character_data.columns)
    fit_character_data = fit_character_data.to_dict(orient='records')

    # 템플릿에 넘겨줄 context
    context = {
        'user' : User,
        'user_name' : user.username,
        'mbti': mbti,
        'user_tag' : user_tag,
        'user_desc' : user_desc,
        'character_data' : character_data,
        'fit_character_data' : fit_character_data,
        'movie_data' : movie_data,
        'tmpusers' : list(tmpusers)[: min(5, len(tmpusers))],
    }

    return render(request, 'common/user_profile.html', context)



def detail_tmpuser(request, tmpuser_id):
    tmpuser = TmpUser.objects.get(id=tmpuser_id)
    user = tmpuser.LoginUser
    mbti = tmpuser.MBTI
    enneagram = tmpuser.ennea_res
    mbti_enneagram = mbti + ' ' + enneagram
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(mbti_enneagram)

    # 유저의 성격 태그
    user_tag = mbti_ennea_df[mbti_ennea_df['MBTI_Enneagram'] == mbti_enneagram]['tag']
    user_tag = " ".join(user_tag.values[0])

    # 유저의 성격 설명
    user_desc = mbti_ennea_df[mbti_ennea_df['MBTI_Enneagram'] == mbti_enneagram]['description'].values[0]


    # 유저가 선호한다고 고른 영화 정보입니다.
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
    data1['CharacterId'] = data1['CharacterId'].map(int)
    data1['hashtag'] = data1.CharacterId.map(characterid_to_hashtag)
    
    data1['Enneagram_sim'] = eval(tmpuser.recommended_character_sim)
    cols=['CharacterId','Character','ko_title','MBTI','img_src','hashtag','npop','Enneagram_sim','name','desc']
    data1 = data1.merge(character_info_df, on='CharacterId')
    data1 = data1[cols][:20].to_dict(orient='records')

    fit_character_ids = tmpuser.fit_character_id
    # data2는 나와 잘맞는 MBTI를 가진 캐릭터 정보 담은 데이터 입니다.
    fit_character_data = pd.DataFrame()
    data2 = pd.DataFrame()
    for id in eval(fit_character_ids):
        data2 = data2.append(character_df[character_df['CharacterId']==int(id)])
    data2['CharacterId'] = data2['CharacterId'].map(int)
    data2['hashtag'] = data2.CharacterId.map(characterid_to_hashtag)
    data2['Enneagram_sim'] = eval(tmpuser.fit_character_sim)
    cols=['CharacterId','Character','ko_title','MBTI','img_src','hashtag','npop','Enneagram_sim','name','desc']
    data2 = data2.merge(character_info_df, on='CharacterId')
    data2 = data2[cols][:20].to_dict(orient='records')
    context = {
        'user' : user,
        'tmpuser' : tmpuser,
        'mbti': mbti,
        'user_tag' : user_tag,
        'user_desc' : user_desc,
        'data1': data1,
        'data2': data2,
        'movie_data' : movie_data,
    }
    return render(request, 'common/detail_tmpuser.html', context)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class TmpUserDeleteView(View):
    def get(self, request, tmpuser_id, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            tmpuser = TmpUser.objects.get(id=tmpuser_id)
            tmpuser.delete()
            return JsonResponse({'message': 'success'})
        return JsonResponse({'message': 'Wrong route'})

# @login_required(login_url='common:login')
# def delete_tmpuser(request, tmpuser_id):
#     tmpuser = TmpUser.objects.get(id=tmpuser_id)
#     tmpuser.delete()
#     return redirect('common:user_profile')


def clean(votes):
    votes = votes[:votes.index("/")]
    if votes[-1] == "k":
        votes = votes[:-1].replace(".","") + "000"
    return int(votes)

# MBTI 상세 페이지 함수
def show_mbti_info(request, mbti):
    get_mbti = mbti

    char_df = character_df[character_df.MBTI==mbti].copy()
    char_df.sort_values('npop',ascending=False,inplace=True)
    char_df[char_df.vote>=1000]
    char_df['hashtag'] = char_df.CharacterId.map(characterid_to_hashtag)
    char_cols=['index','CharacterId','Character','img_src','ko_title','MBTI','hashtag','name','desc']
    char_df = char_df.merge(character_info_df, on='CharacterId').reset_index()
    char_df['index']+=1
    char_list = char_df[char_cols][:200].to_dict(orient='records')    
    context = {
        'mbti' : get_mbti,
        'topten' : char_list[:10],
        'characters':char_list[10:]
    }
    
    return render(request, 'common/mbti_info.html', context)

