from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pandas as pd

from .models import TmpUser
import simplejson as json


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
        enner_list = []
        enner_list.append(ans1)
        user.ennear_ans = json.dumps(enner_list)
        user.save()
    return render(request, 'test_rec/enneagram2.html')

@csrf_exempt
def enneagram_test3(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        ans2 = request.POST.get('enneagram2')
        enner_list = json.loads(user.ennear_ans)
        enner_list.append(ans2)
        user.ennear_ans = json.dumps(enner_list)
        print(user.ennear_ans)
        user.save()
        print(user.ennear_ans)
    engram_crite = ''.join(enner_list)
    df = pd.read_pickle('/opt/ml/input/fighting/Utils/Pickle/enneagram_question.pickle')
    add_quest = df[df.base==engram_crite][['question','three_letter']].copy()
    add_quest_list = add_quest.to_dict(orient='records')
    print(user.ennear_ans)
    return render(request, 'test_rec/enneagram3.html', {'add_quest_list': add_quest_list})

@csrf_exempt
def movie_test(request):
    user = TmpUser.objects.get(id=request.session['user_id'])
    print(f'userid: {user.id}')
    print(f'MBTI:{user.MBTI}')
    print(f'ennear_ans:{user.ennear_ans}')
    print(f'ennear_res:{user.ennear_res}')
    return render(request, 'test_rec/movie.html')

@csrf_exempt
def result_page(request):
    return render(request, 'test_rec/result_bootstrap.html')