from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import simplejson as json
import pandas as pd
import numpy
import pickle
import random
from pathlib import Path
import sys
sys.path.append('..')
from Utils import user_input_to_recommend


pickle_path = Path(__file__).parent.parent.parent.absolute()/"Utils/Pickle"
movieId2poster_path = pickle_path / 'movieid_to_poster_file.pickle'

with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)


ch2mv_path = pickle_path / 'characterId_to_movieId.pickle'
with open(ch2mv_path,'rb') as f:
    characterId_to_movieId = pickle.load(f)


mbti_df = pd.read_pickle(pickle_path / 'MBTI_merge_movieLens_3229_movie.pickle')
movie_genre_plot = pd.read_pickle(pickle_path / 'movie_genre_plot.pickle')


@csrf_exempt
def start_test(request):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    return render(request, 'test_rec/main.html')


@csrf_exempt
def mbti_test(request):
    return render(request, 'test_rec/mbti.html')


@csrf_exempt
def enneagram_test(request):
    if request.method == 'POST':
        request.session['MBTI'] = request.POST.get('MBTI')
    return render(request, 'test_rec/enneagram.html')


@csrf_exempt
def enneagram_test2(request):
    if request.method == 'POST':
        ans1 = request.POST.get('enneagram1')
        request.session['ennear_ans'] = []
        request.session['ennear_ans'].append(ans1)
    return render(request, 'test_rec/enneagram2.html')


@csrf_exempt
def enneagram_test3(request):
    # 이전페이지의 애니어그램 답변2 받아서 세션스토리지에 저장
    if request.method == 'POST':
        ans2 = request.POST.get('enneagram2')
        request.session['ennear_ans'].append(ans2)
        ennear_ans = request.session['ennear_ans']
    # 세션스토리지에 저장된 애니어그램 답변을 바탕으로 추가질문 불러오기
    engram_crite = ''.join(ennear_ans)
    df = pd.read_pickle(pickle_path / 'enneagram_question.pickle')
    add_quest = df[df.base==engram_crite][['question','three_letter']].copy()
    add_quest_list = add_quest.to_dict(orient='records')
    return render(request, 'test_rec/enneagram3.html', {'add_quest_list': add_quest_list})


@csrf_exempt
def movie_test(request):
    # 이전 페이지의 애니어그램 답변3 받아서 세션스토리지에 저장 (1w2 형식)
    if request.method == 'POST':
        ans3 = request.POST.get('enneagram3')
        request.session['ennear_res'] = ans3
    # 추천할 영화리스트 불러오기
    poster_file_list = list(movieId_to_posterfile.values())
    random.seed(14)
    random_poster_file_list = random.sample(poster_file_list, 10)
    context = {
        'movies' : random_poster_file_list,
        'length' : len(random_poster_file_list)
    }
    return render(request, 'test_rec/movie.html', context)


@csrf_exempt
def result_page(request):
    if request.method == 'POST':
        # 이전 페이지의 영화선택 받아서 세션스토리지에 저장
        movies = request.POST.getlist('movies')
        movie_list = [i.split('_')[0] for i in movies]
        request.session['prefer_movie_id'] = movie_list
        # 세션스토리지의 선호 영화리스트를 바탕으로 캐릭터 추천
        movie_list = [int(i) for i in movie_list]
        result = user_input_to_recommend(request.session['MBTI'], request.session['ennear_res'], movie_list)
        result = result[result.Enneagram_sim.notna()]
        result.Enneagram_sim = result.Enneagram_sim.map(lambda x: int(round(x*100)))
        # 추천된 캐릭터 세션스토리지에 저장
        character_list = result['CharacterId'].values.tolist()
        character_list = [str(i) for i in character_list]
        request.session['recommended_character_id'] = character_list
        # 추천된 캐릭터 리스트를 바탕으로 html에 뿌려주기
        cols=['CharacterId','Character','Contents','MBTI','img_src','Enneagram_sim']
        result_list = result[cols].to_dict(orient='records')
        context = {"data": result_list}
        return render(request, 'test_rec/result_bootstrap.html', context)



@csrf_exempt
def result_detail(request):
    return render(request, 'test_rec/result_movie.html')