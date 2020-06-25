from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, redirect
from ucbenik.models import User
from ucbenik.CustomAuth import CustomAuth
from .serializers import UserSerializer

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
        if user is not None:
            request.session['user'] = UserSerializer(user).data
            return redirect("/lesson_one/introduction/page_one")


def update_session(request, what_to_update):
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    request.session[what_to_update] = request.POST['d[' + what_to_update + ']']
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    return HttpResponse('ok')


def introduction_page_one(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_one.html", {"next": "/lesson_one/introduction/page_two", "back": "/", "lesson_one": lesson_one,
                                                                      "lesson": "Lesson 1: About Me", "title": "Introduction", "user": request.session['user']})


def introduction_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_two.html", {"next": "/lesson_one/introduction/page_three",
                                                                      "back": "/lesson_one/introduction/page_one", "lesson_one": lesson_one,
                                                                      "lesson": "Lesson 1: About Me", "title": "Introduction", "user": request.session['user']})


def introduction_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_three.html", {"next": "/lesson_one/introduction/page_four",
                                                                        "back": "/lesson_one/introduction/page_two",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Lesson 1: About Me", "title": "Introduction", "user": request.session['user']})


def introduction_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_four.html", {"next": "/lesson_one/introduction/page_five",
                                                                       "back": "/lesson_one/introduction/page_three",
                                                                       "lesson_one": lesson_one,
                                                                       "lesson": "Lesson 1: About Me", "title": "Introduction", "user": request.session['user']})


def introduction_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_five.html", {"next": "/lesson_one/introduction/page_six",
                                                                       "back": "/lesson_one/introduction/page_four",
                                                                       "lesson_one": lesson_one,
                                                                       "lesson": "Lesson 1: About Me", "title": "Introduction", "user": request.session['user']})


def introduction_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/introduction/page_six.html", {"next": "/lesson_one/exercises/page_one",
                                                                      "back": "/lesson_one/introduction/page_five",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Lesson 1: About Me", "title": "Introduction", "user": request.session['user']})


def exercises_page_one(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_one.html", {"next": "/lesson_one/exercises/page_two",
                                                                   "back": "/lesson_one/introduction/page_six",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Lesson 1: About Me", "title": "Exercises", "user": request.session['user']})


def exercises_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_two.html", {"next": "/lesson_one/exercises/page_three",
                                                                   "back": "/lesson_one/exercises/page_one",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Lesson 1: About Me", "title": "Exercises", "user": request.session['user']})


def exercises_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_three.html", {"next": "/lesson_one/exercises/page_four",
                                                                     "back": "/lesson_one/exercises/page_two",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Lesson 1: About Me", "title": "Exercises", "user": request.session['user']})


def exercises_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_four.html", {"next": "/lesson_one/exercises/page_five",
                                                                    "back": "/lesson_one/exercises/page_three",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Lesson 1: About Me", "title": "Exercises", "user": request.session['user']})


def exercises_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_five.html", {"next": "/lesson_one/exercises/page_six",
                                                                    "back": "/lesson_one/exercises/page_four",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Lesson 1: About Me", "title": "Exercises", "user": request.session['user']})


def exercises_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_six.html", {"next": "/lesson_one/exercises/page_seven",
                                                                   "back": "/lesson_one/exercises/page_five",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Lesson 1: About Me", "title": "Exercises", "user": request.session['user']})


def exercises_page_seven(request):
    if request.method == "GET":
        return render(request, "lesson1/exercises/page_seven.html", {"next": "/lesson_one/character_select/page_one",
                                                                     "back": "/lesson_one/exercises/page_six",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Lesson 1: About Me", "title": "Exercises", "user": request.session['user']})


def character_select_page_one(request):
    if request.method == "GET":
        return render(request, "lesson1/character_select/page_one.html", {"next": "/lesson_one/character_select/page_two",
                                                                          "back": "/lesson_one/exercises/page_seven",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

def character_select_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/character_select/page_two.html", {"next": "character_select/page_three",
                                                                          "back": "/lesson1/character_select/page_one",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

def numbers_page_one(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson1/numbers_select/page_two",
                                                                 "back": "/lesson1/character_select/page_one",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

def numbers_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson1/numbers_select/page_three",
                                                                 "back": "/lesson1/numbers/page_one",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

def numbers_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson1/numbers_select/page_four",
                                                                 "back": "/lesson1/numbers/page_two",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

def numbers_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson1/numbers_select/page_five",
                                                                 "back": "/lesson1/numbers/page_three",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

def numbers_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson1/numbers_select/page_six",
                                                                 "back": "/lesson1/numbers/page_four",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

def numbers_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "#",
                                                                 "back": "/lesson1/numbers/page_five",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})

