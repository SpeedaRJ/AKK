from django.shortcuts import render, redirect
from django.contrib.auth import login
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


def login_page(request):
    if request.method == "GET":
        return render(request, "login.html")
    if request.method == "POST":
        username = request.POST['Email']
        password = request.POST['Password']
        user_check = CustomAuth()
        user = user_check.authenticate(username, password)
        print(user)
        if user is not None:
            print()
            request.session['user'] = user.__dict__
            return redirect("/lesson_one/introduction/page_one")


def introduction_page_one(request):
    print(request.session['user'])
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_one.html", {"next": "/lesson_one/introduction/page_two", "back": "/", "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Introduction"})


def introduction_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_two.html", {"next": "/lesson_one/introduction/page_three",
                                                              "back": "/lesson_one/introduction/page_one", "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Introduction"})


def introduction_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_three.html", {"next": "/lesson_one/introduction/page_four",
                                                              "back": "/lesson_one/introduction/page_two",
                                                                "lesson_one": lesson_one,
                                                                "lesson": "Lesson 1: About Me", "title": "Introduction"})


def introduction_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_four.html", {"next": "/lesson_one/introduction/page_five",
                                                              "back": "/lesson_one/introduction/page_three",
                                                                "lesson_one": lesson_one,
                                                               "lesson": "Lesson 1: About Me", "title": "Introduction"})


def introduction_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_five.html", {"next": "/lesson_one/introduction/page_six",
                                                              "back": "/lesson_one/introduction/page_four",
                                                                "lesson_one": lesson_one,
                                                               "lesson": "Lesson 1: About Me", "title": "Introduction"})


def introduction_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_six.html", {"next": "/lesson_one/exercises/page_one",
                                                              "back": "/lesson_one/introduction/page_five",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Introduction"})


def exercises_page_one(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_one.html", {"next": "/lesson_one/exercises/page_two",
                                                              "back": "/lesson_one/introduction/page_six",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Exercises"})


def exercises_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_two.html", {"next": "/lesson_one/exercises/page_three",
                                                              "back": "/lesson_one/exercises/page_one",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Exercises"})


def exercises_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_three.html", {"next": "/lesson_one/exercises/page_four",
                                                              "back": "/lesson_one/exercises/page_two",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Exercises"})


def exercises_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_four.html", {"next": "/lesson_one/exercises/page_five",
                                                              "back": "/lesson_one/exercises/page_three",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Exercises"})


def exercises_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_five.html", {"next": "/lesson_one/exercises/page_six",
                                                              "back": "/lesson_one/exercises/page_four",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Exercises"})


def exercises_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_six.html", {"next": "/lesson_one/exercises/page_seven",
                                                              "back": "/lesson_one/exercises/page_five",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Exercises"})


def exercises_page_seven(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_seven.html", {"next": "empty",
                                                              "back": "/lesson_one/exercises/page_six",
                                                                "lesson_one": lesson_one,
                                                              "lesson": "Lesson 1: About Me", "title": "Exercises"})
