from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    context = {
        'my_person_list': [],
        'datetime' : ""
    }
    return render(request, 'index.html', context)

@csrf_exempt
def start_test(request):
    return render(request, 'test_rec/main.html')

@csrf_exempt
def mbti_test(request):
    return render(request, 'test_rec/mbti.html')

@csrf_exempt
def enneagram_test(request):
    return render(request, 'test_rec/enneagram.html')

@csrf_exempt
def enneagram_test2(request):
    return render(request, 'test_rec/enneagram2.html')

@csrf_exempt
def enneagram_test3(request):
    add_quest_list = [{'three_letter':1,'question':1},{'three_letter':2,'question':2}]
    return render(request, 'test_rec/enneagram3.html', {'add_quest_list': add_quest_list})

@csrf_exempt
def movie_test(request):
    return render(request, 'test_rec/movie.html')

@csrf_exempt
def result_page(request):
    return render(request, 'test_rec/result_bootstrap.html')