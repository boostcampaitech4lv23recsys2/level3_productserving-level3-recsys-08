from common.forms import UserForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

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


from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'my_person_list': [],
        'datetime' : ""
    }
    return render(request, 'index.html', context)