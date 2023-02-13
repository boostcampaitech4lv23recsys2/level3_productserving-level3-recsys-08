from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.views.decorators.cache import never_cache
import simplejson as json
import pandas as pd
import numpy
import pickle
import random
from pathlib import Path
from .models import TmpUser, CharacterLike
import sys
import json
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

movieId2poster_path = pickle_path / 'movieid_to_poster_file.pickle'
with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)

characterid_to_hashtag_path = pickle_path / '230203_characterid_to_hashtag.pickle'
with open(characterid_to_hashtag_path, 'rb') as f:
    characterid_to_hashtag = pickle.load(f)

fit_mbti_dict_path = pickle_path / '230201_fit_mbti_dict.pickle'
with open(fit_mbti_dict_path, 'rb') as f:
    fit_mbti_dict = pickle.load(f)

mbti_ennea_df_path = pickle_path / 'MBTI_Enneagram_personality_tag.pickle'
with open(mbti_ennea_df_path, 'rb') as f:
    mbti_ennea_df = pickle.load(f)

movie_df = pd.read_pickle(pickle_path / '230213_Popular_movie_1192_cwj.pickle')
character_df = pd.read_pickle(pickle_path / '230213_character_movie_merge.pickle')
character_info_df = pd.read_pickle(pickle_path / '230213_processed_ko_cha_info.pickle')
watch_link =  pd.read_pickle(pickle_path / '230213_watch_link_4679_rows.pickle')
engram_sim = pd.read_pickle(pickle_path / 'enneagram_similarity_075_099.pickle')

def protect_post(response):
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@csrf_exempt
def start_test(request):
    test_count = TmpUser.objects.all().count()
    return render(request, 'test_rec/main.html', {'test_count':test_count} )


@csrf_exempt
def mbti_test(request):
    user = TmpUser.objects.create(create_time=timezone.now())
    request.session['user_id'] = user.id
    return protect_post(render(request, 'test_rec/mbti.html'))


@csrf_exempt
def enneagram_test(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'GET':
        mbti = request.GET.get('MBTI')
        user.MBTI = mbti
        user.save()
    response = render(request, 'test_rec/enneagram.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@csrf_exempt
def enneagram_test2(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'GET':
        ans1 = request.GET.get('enneagram1')
        user.ennea_ans1 = ans1
        user.save()
    response = render(request, 'test_rec/enneagram2.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@csrf_exempt
def enneagram_test3(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    # 이전페이지의 애니어그램 답변2 받아서 유저정보에 저장
    if request.method == 'GET':
        ans2 = request.GET.get('enneagram2')
        user.ennea_ans2 = ans2
        user.save()
    # 유저정보에 저장된 애니어그램 답변을 바탕으로 추가질문 불러오기
    engram_crite = user.ennea_ans1 + user.ennea_ans2
    df = pd.read_pickle(pickle_path / 'enneagram_question.pickle')
    add_quest = df[df.base==engram_crite][['question','three_letter']].copy()
    add_quest_list = add_quest.to_dict(orient='records')
    return render(request, 'test_rec/enneagram3.html', {'add_quest_list': add_quest_list})


@csrf_exempt
def movie_test(request):
    
    user = TmpUser.objects.get(id=request.session['user_id'])

    # 이전 페이지의 애니어그램 답변3 받아서 유저정보에 저장 (1w2 형식)
    if request.method == 'GET':
        ans3 = request.GET.get('enneagram3')
        if ans3==None: # 영화 무한 스크롤 하는 경우
            pass
        else:
            user.ennea_res = ans3
            user.save()

    # 추천할 영화리스트 불러오기
    N_movies=100
    seed = random.randint(0,int(1e6))
    print(f">>>{seed = }")
    selec_movie_ids = list(set(final_movie_select(seed, N_movies)))
    selec_movie_ids = movie_df[movie_df.movieId.isin(selec_movie_ids)].movieId.tolist()
    print(f">>>>>>>>>>>>>{len(selec_movie_ids)}")
    poster_file_list = [movieId_to_posterfile[id] for id in selec_movie_ids]
    print(f"{len(selec_movie_ids)=},  {len(poster_file_list)=}, {len(set(poster_file_list))=}")
    paginator1 = Paginator(poster_file_list, 20)
    page_number = request.GET.get('page') or 1
    page_obj1 = paginator1.get_page(page_number)

    movieid2kotitle = dict(zip(movie_df.movieId, movie_df.ko_title))
    ko_title_list = [movieid2kotitle[id] for id in selec_movie_ids]
    paginator2 = Paginator(ko_title_list, 20)
    page_number = request.GET.get('page') or 1
    page_obj2 = paginator2.get_page(page_number)

    ziped_page_obj = zip(page_obj1, page_obj2)

    context = {
        'length' : len(poster_file_list),
        'page_obj': page_obj1,
        'zip_page_obj': ziped_page_obj
    }
    return render(request, 'test_rec/movie.html', context)


@csrf_exempt
def result_page(request):

    user = TmpUser.objects.get(id=request.session['user_id'])
    mbti = user.MBTI
    enneagram = user.ennea_res
    mbti_enneagram = mbti + ' ' + enneagram
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(mbti_enneagram)

    # 유저의 성격 태그
    user_tag = mbti_ennea_df[mbti_ennea_df['MBTI_Enneagram'] == mbti_enneagram]['tag']
    user_tag = " ".join(user_tag.values[0])

    # 유저의 성격 설명
    user_desc = mbti_ennea_df[mbti_ennea_df['MBTI_Enneagram'] == mbti_enneagram]['description'].values[0]

    # print(">>>>>>>>>>>>>>",request.POST.getlist('movies'))
    if request.method == 'GET':
        # 이전 페이지의 영화선택 받아서 유저정보에 저장
        movies = request.GET.getlist('movies')
        movie_list = [i.split('_')[0] for i in movies]
        print(f"{movie_list=}")
        if movie_list:
            user.prefer_movie_id = json.dumps(movie_list)
            # 유저정보가 선호한 영화리스트를 바탕으로 캐릭터 추천
            movie_list = [int(i) for i in movie_list]
            
            interaction_movie_list = [i for i in movie_list if i < 300_000]
            side_info_movie_list = [i for i in movie_list if i >= 300_000]
            user_fit_MBTI = fit_mbti_dict[user.MBTI]
            mbti_list=[user.MBTI, user_fit_MBTI]
            result=pd.DataFrame()
            ratio_string=''
            if interaction_movie_list: # 2019년 까지의 영화를 고른 경우
                result1 = user_input_to_recommend(mbti_list, user.ennea_res, interaction_movie_list, 100)
                result = pd.concat([result, result1])
                print('>>>>',result1.shape)
                annoy_recommend = result1.movieId.drop_duplicates().tolist()
                user.annoy_recommend_movies = annoy_recommend
                ratio_string+=f"{len(annoy_recommend)}:"
            else: # 2019년 까지의 영화를 고르지 않은 경우
                ratio_string+="0:"
            if side_info_movie_list: # 2020년 이후 영화 고른 경우
                result2 = user_input_to_side_recommend(mbti_list, user.ennea_res, side_info_movie_list, 100)
                result = pd.concat([result, result2])
                print('>>>>',result2.shape)
                bts_recommend = result2.movieId.drop_duplicates().tolist()
                user.bts_recommend_movies = bts_recommend
                ratio_string+=f"{len(bts_recommend)}"
            else: # 2020년 이후 영화를 고르지 않은 경우
                ratio_string+="0"
            user.annoy_bts_ratio=ratio_string
            print(f"{ratio_string = }")
            print(f"{result.movieId.nunique()=} {result.shape=}")
            result.drop_duplicates('CharacterId',inplace=True)
            result = result[result.Enneagram_sim.notna()]
            result.Enneagram_sim = result.Enneagram_sim.map(lambda x: int(round(x*100)))

            # 추천된 캐릭터 리스트를 바탕으로 html에 뿌려주기
            cols=['CharacterId','Character','ko_title','MBTI','img_src','hashtag','npop','Enneagram_sim','name','desc']
            result = result.merge(movie_df[['movieId','ko_title','npop']])
            result['hashtag'] = result.CharacterId.map(characterid_to_hashtag)
            # 캐릭터 한글 이름 추가
            result = result.merge(character_info_df, on='CharacterId')
            ## 나와 잘맞는 MBTI도 유사도 낮추기
            result.sort_values('Enneagram_sim',ascending=False,inplace=True)
            print(result[cols][:3])
            # 나와 유사한 캐릭터 결과
            result_list = result[result.MBTI==user.MBTI][cols][:20].to_dict(orient='records')
            paginator = Paginator(result_list, 20)
            page_number = request.GET.get('page') or 1
            page_obj = paginator.get_page(page_number)
            # 나와 잘맞는 캐릭터 결과
            result_list2 = result[result.MBTI==user_fit_MBTI][cols][:20].to_dict(orient='records')
            print(f"{len(result) = } , {len(result_list) = }, {len(result_list2) = }")
            # 추천된 캐릭터결과 저장
            for_save_sim_character_df = result[result['MBTI']==user.MBTI][:20]
            for_save_fit_character_df = result[result['MBTI']==user_fit_MBTI][:20]
            # 추천된 캐릭터 결과 저장 - 나와 같은 MBTI 캐릭터 id
            similar_character_list = for_save_sim_character_df['CharacterId'].values.tolist()
            similar_character_list = [str(i) for i in similar_character_list]
            user.recommended_character_id = json.dumps(similar_character_list)
            # 추천된 캐릭터 결과 저장 - 나와 같은 MBTI 캐릭터 유사도
            similar_character_sim = for_save_sim_character_df['Enneagram_sim'].values.tolist()
            similar_character_sim = [str(i) for i in similar_character_sim]
            user.recommended_character_sim = json.dumps(similar_character_sim)
            # 추천된 캐릭터 결과 저장 - 나와 잘 맞는 MBTI 캐릭터 id
            fit_character_list = for_save_fit_character_df['CharacterId'].values.tolist()
            fit_character_list = [str(i) for i in fit_character_list]
            user.fit_character_id = json.dumps(fit_character_list)
            # 추천된 캐릭터 결과 저장 - 나와 잘 맞는 MBTI 캐릭터 유사도
            fit_character_sim = for_save_fit_character_df['Enneagram_sim'].values.tolist()
            fit_character_sim = [str(i) for i in fit_character_sim]
            user.fit_character_sim = json.dumps(fit_character_sim)
            user.save()
            
            # 로그인 되었다면 TmpUser 객체 로그인 유저와 연결
            if request.user.is_authenticated:  #로그인이 되어있는지 확인
                print('로그인 OK')
                if check_TmpUserInfo(request): #테스트를 마쳤는지 확인
                    print('TmpUser 객체 OK')
                    login_user = request.user        #로그인한 유저의 정보를 가져옴
                    user.LoginUser = login_user   #로그인한 유저의 정보를 TmpUser 객체에 저장 -> 로그인유저와 tmp유저 연결됨
                    user.save()
            
            feedback=''
            context = {
                        "data1": result_list,
                        'data2':result_list2, 
                        'page_obj': page_obj, 
                        'tmpuser':user, 
                        'feedback':feedback,
                        'user_tag':user_tag,
                        'user_desc':user_desc
                      }
            return render(request, 'test_rec/result.html', context)
        else:
            return render(request, 'test_rec/result.html')


@csrf_exempt
def result_movie(request, character_id):
    
    try:
        # 테스트 완료 했을 때 - 로그인 여부 상관없음
        user = TmpUser.objects.get(id=request.session['user_id'])
        login_user = request.user.id
        print(f"테스트 완료: {user.LoginUser_id=} {login_user=}")
    except:
        # 테스트 완료 안했을 때 - 인덱스에서 바로 들어왔을 때
        # user = TmpUser.objects.get(id=request.session['user_id'])
        user = None
        login_user = request.user.id
        print(f"테스트 안했을 때: {user=} {login_user=}")
    need_cols=['Character','movieId']
    character_name, movie_id = character_df[character_df.CharacterId==int(character_id)][need_cols].values[0]
    character_name = character_info_df[character_info_df.CharacterId==int(character_id)][['name']].values[0][0]
    char_df = character_df[character_df.movieId==movie_id].copy()

    if user:
        user_enn = user.ennea_res
        user_fit_MBTI = fit_mbti_dict[user.MBTI]
        mbti_list=[user.MBTI,user_fit_MBTI]
        print(f"{mbti_list=}")
        try:
            char_df['Enneagram_sim'] = char_df.Enneagram.map(get_en_sim(user_enn,engram_sim))
            char_df.Enneagram_sim = char_df.Enneagram_sim.map(lambda x: int(round(x*100)))
        except:
            breakpoint()

    ## hashtag
    char_df['hashtag'] = char_df.CharacterId.map(characterid_to_hashtag)
    posterfile_path = movieId_to_posterfile[movie_id]
    movie_title, genres, plot = movie_df[movie_df.movieId==movie_id][['ko_title','ko_genre','ko_plot']].values[0]
    # characters = character_df[character_df.movieId==movie_id]
    result_movie ={
        'name': character_name,
        'movie' : movie_title,
        'img_path' : posterfile_path,
        'genres' : genres,
        'plot' : plot
    }

    if user:
        char_cols=['CharacterId','Character','img_src','ko_title','MBTI','hashtag','Enneagram_sim','name','desc']
        char_df.sort_values('Enneagram_sim',ascending=False,inplace=True)
    else:
        char_cols=['CharacterId','Character','img_src','ko_title','MBTI','hashtag','name','desc']
    # print(result_movie)

    links_df = watch_link[watch_link.movieId==movie_id][['platform','link']]
    links = links_df.to_dict(orient='records')

    #캐릭터 한글 이름, 설명 붙이기
    char_df = char_df.merge(character_info_df, on='CharacterId')
    cur_char_df = char_df[char_df.CharacterId==int(character_id)]
    print(cur_char_df[char_cols])
    cur_character = cur_char_df[char_cols].to_dict(orient='records')[0]
    # cur_character['char_info'] = character_info_df[character_info_df.CharacterId==int(character_id)]['desc'].values[0]
    # cur_character['char_name'] = character_info_df[character_info_df.CharacterId==int(character_id)]['name'].values[0]
    
    # 작품에 등장한 다른 캐릭터
    char_df = char_df[char_df.CharacterId!=int(character_id)]
    if len(char_df)==0:
        char_data = []
    else:
        char_data = char_df[char_cols].to_dict(orient='records')

    liked = 0
    # 로그인 유저인 경우 해당 캐릭터 좋아요 눌렀는지 여부
    if login_user:
        character_like = CharacterLike.objects.filter(Q(LoginUser_id=login_user) & Q(character_id=character_id))
        if len(character_like):
            liked=1
    # 로그인 유저인 경우 해당 캐릭터가 받은 좋아요 수
    cur_character_like = CharacterLike.objects.filter(character_id=character_id)
    like_cnt = len(cur_character_like)
    context = {'user1' : user, 'login_user': login_user, 'liked':liked, 'data': result_movie, 'links': links, 'cur_character':cur_character, 'char_data':char_data, "like_cnt":like_cnt}
    return render(request, 'test_rec/result_movie.html', context)

# 좋아요
@csrf_exempt
def like_character(request, character_id, user_id):
    print(f">>> {request.user.id=}")
    login_user_id = request.user.id
    liked=0
    # 로그인 유저
    if login_user_id:
        # 이미 user가 해당 캐릭터 좋아요 누른 경우
        character_like = CharacterLike.objects.filter(Q(LoginUser_id=login_user_id) & Q(character_id=character_id))
        # 처음 user가 해당 캐릭터 좋아요 누른 경우
        if len(character_like)==0:
            new_character_like = CharacterLike.objects.create(LoginUser_id=login_user_id, character_id=character_id, create_time=timezone.now())
            liked=1
        # user가 이미 좋아요 누른 캐릭터 다시 좋아요 누른 경우 -> 해제
        else:
            # 좋아요 삭제
            character_like.delete()
            liked=0

    cur_character_like = CharacterLike.objects.filter(character_id=character_id)
    cur_character_like_cnt = len(cur_character_like)
    print(f"{login_user_id=}의 해당 캐릭터({character_id}) 좋아요: {liked}, 그래서 해당 캐릭터 좋아요 수는 {cur_character_like_cnt}")
    context={
        'like_cnt':cur_character_like_cnt,
        'liked':liked
    }
    response = JsonResponse(context)
    return response

# 피드백
@csrf_exempt
def feedback_result(request, user_id):
    user = TmpUser.objects.get(id=request.session['user_id'])
    before_user_feedback = user.feedback
    print(f"{before_user_feedback = }")
    if request.method == 'POST':
        # data = json.loads(request.body)
        value = request.POST.get('value')
        context={
            'feedback':0
        }
        if value == '+': # 좋아요를 눌렀을 떄,
            if before_user_feedback != 1: # 기존에 선택 안함 or 싫어요
                user.feedback = 1
                print('good')
            elif before_user_feedback == 1: # 기존에 좋아요 누른 경우
                user.feedback = 0
                print("No eval")
            context['feedback'] = '+'
        elif value == '-': # 싫어요를 눌렀을 때,
            if before_user_feedback != -1: # 기존에 선택 안함 or 좋아요
                user.feedback = -1
                print('bad')
            elif before_user_feedback == -1: # 기존에 싫어요 누른 경우
                user.feedback = 0
                print("No eval")
            context['feedback'] = '-'
        user.save()
    
    response = JsonResponse(context)
    return response