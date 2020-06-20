from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    if request.method == 'GET':
        print('Hello')
        return render(request, 'main.html')
    elif not request.user.is_authenticated:
        return redirect('register')


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method =='POST':
        print("Hello")

def login(request):
    if request.method == "GET":
        return render(request, "login.html")