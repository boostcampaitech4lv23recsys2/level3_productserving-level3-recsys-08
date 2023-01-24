from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'my_person_list': [],
        'datetime' : ""
    }
    return render(request, 'index.html', context)