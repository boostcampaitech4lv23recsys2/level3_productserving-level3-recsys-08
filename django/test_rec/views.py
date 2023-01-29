from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import simplejson as json
import pandas as pd
import numpy
import pickle
import random
from pathlib import Path
from .models import TmpUser
import sys
sys.path.append('..')
from Utils import user_input_to_recommend, movie_select_2


def print_TmpUserInfo(user):
    print(f'userid: {user.id}')
    print(f'MBTI:{user.MBTI}')
    print(f'ennea_ans1:{user.ennea_ans1}')
    print(f'ennea_ans2:{user.ennea_ans2}')
    print(f'ennea_res:{user.ennea_res}')
    print(f'prefer_movie_id:{user.prefer_movie_id}')
    print(f'recommended_character_id:{user.recommended_character_id}')

pickle_path = Path(__file__).parent.parent.parent.absolute()/"Utils/Pickle"
movieId2poster_path = pickle_path / 'movieid_to_poster_file.pickle'


with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)


ch2mv_path = pickle_path / 'characterId_to_movieId.pickle'
with open(ch2mv_path,'rb') as f:
    characterId_to_movieId = pickle.load(f)


mbti_df = pd.read_pickle(pickle_path / 'MBTI_merge_movieLens_3229_movie.pickle')
movie_genre_plot = pd.read_pickle(pickle_path / 'movie_genre_plot.pickle')
watch_link =  pd.read_pickle(pickle_path / 'watch_link_3229movie_4462_rows.pickle')


@csrf_exempt
def start_test(request):
    return render(request, 'test_rec/main.html')


@csrf_exempt
def mbti_test(request):
    user = TmpUser.objects.create(create_time=timezone.now())
    request.session['user_id'] = user.id
    return render(request, 'test_rec/mbti.html')


@csrf_exempt
def enneagram_test(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        mbti = request.POST.get('MBTI')
        user.MBTI = mbti
        user.save()
    return render(request, 'test_rec/enneagram.html')


@csrf_exempt
def enneagram_test2(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        ans1 = request.POST.get('enneagram1')
        user.ennea_ans1 = ans1
        user.save()
    return render(request, 'test_rec/enneagram2.html')


@csrf_exempt
def enneagram_test3(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    # 이전페이지의 애니어그램 답변2 받아서 유저정보에 저장
    if request.method == 'POST':
        ans2 = request.POST.get('enneagram2')
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
    if request.method == 'POST':
        ans3 = request.POST.get('enneagram3')
        user.ennea_res = ans3
        user.save()
    # 추천할 영화리스트 불러오기
    seed = random.randint(0,int(1e6))
    print(f">>>{seed = }")
    selec_movie_ids = movie_select_2(seed, 20)
    poster_file_list = [movieId_to_posterfile[id] for id in selec_movie_ids]
    context = {
        'movies' : poster_file_list,
        'length' : len(poster_file_list)
    }
    return render(request, 'test_rec/movie.html', context)


@csrf_exempt
def result_page(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        # 이전 페이지의 영화선택 받아서 유저정보에 저장
        movies = request.POST.getlist('movies')
        movie_list = [i.split('_')[0] for i in movies]
        user.prefer_movie_id = json.dumps(movie_list)
        # 유저정보가 선호한 영화리스트를 바탕으로 캐릭터 추천
        movie_list = [int(i) for i in movie_list]
        result = user_input_to_recommend(user.MBTI, user.ennea_res, movie_list, 60)
        result = result[result.Enneagram_sim.notna()]
        result.Enneagram_sim = result.Enneagram_sim.map(lambda x: int(round(x*100)))
        # 추천된 캐릭터 유저정보에 저장
        character_list = result['CharacterId'].values.tolist()
        character_list = [str(i) for i in character_list]
        user.recommended_character_id = json.dumps(character_list)
        user.save()
        # 추천된 캐릭터 리스트를 바탕으로 html에 뿌려주기
        cols=['CharacterId','Character','Contents','MBTI','img_src','Enneagram_sim']
        result_list = result[cols].to_dict(orient='records')
        context = {"data": result_list}

        return render(request, 'test_rec/result.html', context)


@csrf_exempt
def result_movie(request, character_id):
    need_cols=['Character','Contents','movieId']
    character_name, movie_title, movie_id = mbti_df[mbti_df.CharacterId==int(character_id)][need_cols].values[0]
    posterfile_path = movieId_to_posterfile[movie_id]
    genres, plot = movie_genre_plot[movie_genre_plot.movieId==movie_id][['ko_genres','ko_plot']].values[0]
    result_movie ={
        'name': character_name,
        'movie' : movie_title,
        'img_path' : posterfile_path,
        'genres' : genres,
        'plot' : plot
    }
    # print(result_movie)
    links_df = watch_link[watch_link.movieId==movie_id][['platform','link']]
    links = links_df.to_dict(orient='records')
    # print(links)
    context = {'data': result_movie, 'links': links}
    return render(request, 'test_rec/result_movie.html', context)
