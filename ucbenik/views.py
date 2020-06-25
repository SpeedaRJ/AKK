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
        return render(request, "lesson1/character_select/page_two.html", {"next": "/lesson_one/character_select/page_three",
                                                                          "back": "/lesson1/character_select/page_one",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def character_select_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/character_select/page_three.html", {"next": "/lesson_one/character_select/page_four",
                                                                          "back": "/lesson1/character_select/page_two",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def character_select_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/character_select/page_four.html", {"next": "/lesson_one/character_select/page_five",
                                                                          "back": "/lesson1/character_select/page_three",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def character_select_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/character_select/page_five.html", {"next": "/lesson_one/character_select/page_six",
                                                                          "back": "/lesson1/character_select/page_four",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def character_select_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/character_select/page_six.html", {"next": "/lesson_one/numbers/page_one",
                                                                          "back": "/lesson1/character_select/page_five",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_one(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson1/numbers/page_two",
                                                                 "back": "/lesson1/character_select/page_six",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_two.html", {"next": "/lesson1/numbers/page_three",
                                                                 "back": "/lesson1/numbers/page_one",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_three.html", {"next": "/lesson1/numbers/page_four",
                                                                 "back": "/lesson1/numbers/page_two",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_four.html", {"next": "/lesson1/numbers/page_five",
                                                                 "back": "/lesson1/numbers/page_three",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_five.html", {"next": "/lesson1/numbers/page_six",
                                                                 "back": "/lesson1/numbers/page_four",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_six.html", {"next": "/lesson1/numbers/page_seven",
                                                                 "back": "/lesson1/numbers/page_five",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_seven(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_seven.html", {"next": "/lesson1/numbers/page_eight",
                                                                 "back": "/lesson1/numbers/page_six",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_eight(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_eight.html", {"next": "/lesson1/numbers/page_nine",
                                                                 "back": "/lesson1/numbers/page_seven",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_nine(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_nine.html", {"next": "/lesson1/numbers/page_ten",
                                                                 "back": "/lesson1/numbers/page_seven",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_ten(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_ten.html", {"next": "/lesson1/numbers/page_eleven",
                                                                 "back": "/lesson1/numbers/page_nine",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_eleven(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_eleven.html", {"next": "/lesson1/numbers/page_twelve",
                                                                 "back": "/lesson1/numbers/page_ten",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_twelve(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_twelve.html", {"next": "/lesson1/numbers/page_tirteen",
                                                                 "back": "/lesson1/numbers/page_eleven",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_thirteen(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_thirteen.html", {"next": "/lesson1/numbers/page_fourteen",
                                                                 "back": "/lesson1/numbers/page_twelve",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_fourteen(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_fourteen.html", {"next": "/lesson1/numbers/page_fifteen",
                                                                 "back": "/lesson1/numbers/page_thirteen",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_fifteen(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_fifteen.html", {"next": "/lesson1/numbers/page_sixteen",
                                                                 "back": "/lesson1/numbers/page_fourteen",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_sixteen(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_sixteen.html", {"next": "/lesson1/numbers/page_seventeen",
                                                                 "back": "/lesson1/numbers/page_fifteen",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_seventeen(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_seventeen.html", {"next": "/lesson1/numbers/page_eighteen",
                                                                 "back": "/lesson1/numbers/page_sixteen",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_eighteen(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_eighteen.html", {"next": "/lesson1/numbers/page_nineteen",
                                                                 "back": "/lesson1/numbers/page_seventeen",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_nineteen(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_nineteen.html", {"next": "/lesson1/numbers/page_twenty",
                                                                 "back": "/lesson1/numbers/page_eighteen",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_twenty(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_twenty.html", {"next": "/lesson1/numbers/page_twentyone",
                                                                 "back": "/lesson1/numbers/page_nineteen",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_twentyone(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_twentyone.html", {"next": "/lesson1/numbers/page_twentytwo",
                                                                 "back": "/lesson1/numbers/page_twenty",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def numbers_page_twentytwo(request):
    if request.method == "GET":
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson1/colors/page_one",
                                                                 "back": "/lesson1/numbers/page_twentyone",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Avatar", "user": request.session['user']})


def colors_page_one(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_one.html", {"next": "/lesson1/numbers/page_two.html",
                                                                 "back": "/lesson1/numbers/page_twentytwo.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_two(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_two.html", {"next": "/lesson1/colors/page_three.html",
                                                                 "back": "/lesson1/colors/page_one.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_three(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_three.html", {"next": "/lesson1/colors/page_four.html",
                                                                 "back": "/lesson1/colors/page_two.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_four(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_four.html", {"next": "/lesson1/colors/page_five.html",
                                                                 "back": "/lesson1/colors/page_three.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_five(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_five.html", {"next": "/lesson1/colors/page_six.html",
                                                                 "back": "/lesson1/colors/page_four.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_six(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_six.html", {"next": "/lesson1/colors/page_seven.html",
                                                                 "back": "/lesson1/colors/page_five.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_seven(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_seven.html", {"next": "/lesson1/colors/page_eight.html",
                                                                 "back": "/lesson1/colors/page_six.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_eight(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_eight.html", {"next": "/lesson1/colors/page_nine.html",
                                                                 "back": "/lesson1/colors/page_seven.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


def colors_page_nine(request):
    if request.method == "GET":
        return render(request, "lesson1/colors/page_nine.html", {"next": "/#",
                                                                 "back": "/lesson1/colors/page_nine.html",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Lesson 1: About Me", "title": "Colors", "user": request.session['user']})


