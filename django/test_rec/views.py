from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import simplejson as json
import pandas as pd
import pickle
import random

from .models import TmpUser
import sys
sys.path.append('..')
from Utils import user_input_to_recommend


movieId2poster_path='/opt/ml/input/fighting/Utils/Pickle/movieid_to_poster_file.pickle'
with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)

ch2mv_path='/opt/ml/input/fighting/Utils/Pickle/characterId_to_movieId.pickle'
with open(ch2mv_path,'rb') as f:
    characterId_to_movieId = pickle.load(f)

mbti_df = pd.read_pickle('/opt/ml/input/fighting/Utils/Pickle/MBTI_merge_movieLens_3229_movie.pickle')
movie_genre_plot = pd.read_csv('/opt/ml/input/fighting/Data/DataProcessing/movie_genre_plot.csv')

@csrf_exempt
def start_test(request):
    user = TmpUser.objects.create(create_time=timezone.now())
    request.session['user_id'] = user.id
    return render(request, 'test_rec/main.html')


@csrf_exempt
def mbti_test(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
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
        ennear_list = []
        ennear_list.append(ans1)
        user.ennear_ans = json.dumps(ennear_list)
        user.save()
    return render(request, 'test_rec/enneagram2.html')

@csrf_exempt
def enneagram_test3(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        ans2 = request.POST.get('enneagram2')
        ennear_list = json.loads(user.ennear_ans)
        ennear_list.append(ans2)
        user.ennear_ans = json.dumps(ennear_list)
        user.save()
    engram_crite = ''.join(ennear_list)
    df = pd.read_pickle('/opt/ml/input/fighting/Utils/Pickle/enneagram_question.pickle')
    add_quest = df[df.base==engram_crite][['question','three_letter']].copy()
    add_quest_list = add_quest.to_dict(orient='records')
    print(user.ennear_ans)
    return render(request, 'test_rec/enneagram3.html', {'add_quest_list': add_quest_list})

@csrf_exempt
def movie_test(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        ans3 = request.POST.get('enneagram3')
        user.ennear_res = ans3
        user.save()
    
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
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        movies = request.POST.getlist('movies')
        movie_list = [int(i.split('_')[0]) for i in movies]
        user.prefer_movie_id = json.dumps(movie_list)

        result = user_input_to_recommend(user.MBTI, user.ennear_res, movie_list)
        result = result[result.Enneagram_sim.notna()]
        # user.save()
    # print(f'userid: {user.id}')
    # print(f'MBTI:{user.MBTI}')
    # print(f'ennear_ans:{user.ennear_ans}')
    # print(f'ennear_res:{user.ennear_res}')
    # print(f'prefer_movie_id:{user.prefer_movie_id}')
    return render(request, 'test_rec/result_bootstrap.html')