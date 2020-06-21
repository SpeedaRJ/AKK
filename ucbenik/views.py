from django.shortcuts import render, redirect
from ucbenik.models import User
from ucbenik.CustomAuth import CustomAuth

lesson_one = {"Introduction": "introduction", "Exercises": "exercises", "Avatar": "avatar", "Numbers": "numbers",
              "Colors": "colors", "Years": "years"}


# Create your views here.
def home(request):
    if request.method == 'GET':
        return render(request, 'home.html')
    elif not request.user.is_authenticated:
        return redirect('register')


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        email = request.POST['Email']
        password = request.POST['Password']
        First_name = request.POST['Name']
        Age = request.POST['Age']
        Sex = request.POST['Sex']
        User.objects.create_user(email, password, First_name, Age, Sex)


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    if request.method == "POST":
        username = request.POST['Email']
        password = request.POST['Password']
        user_check = CustomAuth()
        user = user_check.authenticate(username, password)
        print(user)
        if user is not None:
            return redirect("/")


def introduction(request):
    if request.method == "GET":
        return render(request, "introduction.html", lesson_one)