from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, redirect
from ucbenik.models import User, CharacterDataMen, CharacterDataWomen
from ucbenik.CustomAuth import CustomAuth
from .serializers import UserSerializer

lesson_one = {"Introduction": "/lesson_one/introduction/page_one", "Appearance": "/lesson_one/character_select/page_one",
              "Numbers": "/lesson_one/numbers/page_one", "Colors": "/lesson_one/colors/page_one", "Years": "/lesson_one/years/page_one",
              "Personal traits": "/lesson_one/personal_traits/page_one", "He she it": "/lesson_one/he_she_it/page_one"}


def index(request):
    if 'user' in request.session:
        return redirect('lesson_one/title')
    return redirect('login')

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
        first_name = request.POST['Name']
        age = request.POST['Age']
        sex = request.POST['Sex']
        try:
            user = User.objects.create_user(email, password, first_name, age, sex)
        except:
            context = {'email_in_use': 'Račun s tem email-om že obstaja.',
                       'name' : first_name,
                       'age' : age,
                       'sex' : sex
                       }
            return render(request, 'register.html' , context)
        if user is not None:
            request.session.flush()
            request.session['user'] = UserSerializer(user).data
            return redirect("/lesson_one/introduction/page_one")
    return redirect("register")

def login_page(request):
    if request.method == "GET":
        return render(request, "login.html")
    if request.method == "POST":
        username = request.POST['Email']
        password = request.POST['Password']
        user_check = CustomAuth()
        user = user_check.authenticate(request, username, password)
        if user is not None:
            request.session.flush()
            request.session['user'] = UserSerializer(user).data
            if user.last_page:
                return redirect(user.last_page)
            else: 
                return redirect('/')
        elif user is None:
            context = {'no_user': 'Napačno uporabniško ime ali geslo',
                       'username' : username }
            return render(request, "login.html", context)

def logout(request):
    if request.method == "GET":
        try:
            user = User.objects.get(email=request.session['user']['email'])
            user.set_last_page(request.META['QUERY_STRING'])
        except:
            print("logout without user??")
        request.session.flush()
        return redirect("/")

def update_session(request, what_to_update):
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    if what_to_update in request.session:
        del request.session[what_to_update]
        request.session[what_to_update] = request.POST['d[' + what_to_update + ']']
    else:
        request.session[what_to_update] = request.POST['d[' + what_to_update + ']']
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    return HttpResponse('ok')

def save_session(request):
    if request.session['user']['sex'] == "M":
        cs = CharacterDataMen(
            user=User.objects.get_by_natural_key(request.session['user']['email']),
            neck=request.session['neck'],
            body_color=request.session['body_color'],
            height=request.session['height'],
            body_type=request.session['body_type'],
            hair_color=request.session['hair_color'],
            glasses=request.session['glasses'],
            beard=request.session['beard'],
            hair_type=request.session['hair_type'],
            suite_color=request.session['suite_color']
        )
    else:
        if request.session['wearing'] == "dress":
            cs = CharacterDataWomen(
                user=User.objects.get_by_natural_key(request.session['user']['email']),
                neck=request.session['neck'],
                body_color=request.session['body_color'],
                height=request.session['height'],
                body_type=request.session['body_type'],
                hair_color=request.session['hair_color'],
                glasses=request.session['glasses'],
                dress_color=request.session['dress_color'],
                shoes_color=request.session['shoes_color'],
                hair_type=request.session['hair_type'],
            )
        else:
            cs = CharacterDataWomen(
                user=User.objects.get_by_natural_key(request.session['user']['email']),
                neck=request.session['neck'],
                body_color=request.session['body_color'],
                height=request.session['height'],
                body_type=request.session['body_type'],
                hair_color=request.session['hair_color'],
                glasses=request.session['glasses'],
                shoes_color=request.session['shoes_color'],
                pants_color=request.session['pants_color'],
                shirt_color=request.session['shirt_color'],
                hair_type=request.session['hair_type'],
            )
    try:
        cs.save()
        return HttpResponse('ok')
    except NameError:
        print(NameError)
        return HttpResponse('error')

def getColorsAndParts(data_set, sex):
    if sex == "M":
        if data_set.beard == "full_beard":
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
                "beard": "[id^=Brki],[id^=Brada]",
                "Krog": "[id^=Krog]",
                "Pulover": "[id^=Pulover]"
            }
        elif data_set.beard == "full_beard" or "mustache" or data_set.beard == "goatee":
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
                "beard": "[id^=Brki]",
                "Krog": "[id^=Krog]",
                "Pulover": "[id^=Pulover]"
            }
        elif data_set.beard == "no_beard":
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
                "Krog": "[id^=Krog]",
                "Pulover": "[id^=Pulover]"
            }
        colors = {
            "body_color": data_set.body_color,
            "neck": data_set.neck,
            "hair_color": data_set.hair_color,
            "suite_color": data_set.suite_color
        }
        return parts, colors

    else:
        if data_set.wearing == "dress":
            colors = {
                "body_color": data_set.body_color,
                "neck": data_set.neck,
                "hair_color": data_set.hair_color,
                "suite_color": data_set.dress_color
            }
        else:
            colors = {
                "body_color": data_set.body_color,
                "neck": data_set.neck,
                "hair_color": data_set.hair_color,
                "suite_color": data_set.shirt_color
            }
        parts = {
            "body_color": "[id^=Koza]",
            "neck": "[id^=Vrat]",
            "hair_color": "[id^=Lasje]",
            "shirt_color": "[id^=Majica]",
            "Krog": "[id^=Krog]",
        }
        return parts, colors


def lesson_one_title(request):
    if request.method == "GET":
        return render(request, "lesson1/title_page.html", {"next": "/lesson_one/introduction/page_one", "back": "/", "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "", "user": request.session['user']})



def introduction_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/introduction/page_one.html", {"next": "/lesson_one/introduction/page_two", "back": "/", "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})



def introduction_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/introduction/page_two.html", {"next": "/lesson_one/introduction/page_three",
                                                                      "back": "/lesson_one/introduction/page_one", "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})

def introduction_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/introduction/page_three.html", {"next": "/lesson_one/introduction/page_four",
                                                                        "back": "/lesson_one/introduction/page_two",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})

def introduction_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/introduction/page_four.html", {"next": "/lesson_one/introduction/page_five",
                                                                       "back": "/lesson_one/introduction/page_three",
                                                                       "lesson_one": lesson_one,
                                                                       "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})

def introduction_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/introduction/page_five.html", {"next": "/lesson_one/introduction/page_six",
                                                                       "back": "/lesson_one/introduction/page_four",
                                                                       "lesson_one": lesson_one,
                                                                       "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})

def introduction_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/introduction/page_six.html", {"next": "/lesson_one/introduction/page_seven",
                                                                      "back": "/lesson_one/introduction/page_five",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})

def introduction_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/introduction/page_seven.html", {"next": "/lesson_one/exercises/page_one",
                                                                      "back": "/lesson_one/introduction/page_six",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})

def exercises_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/exercises/page_one.html", {"next": "/lesson_one/exercises/page_two",
                                                                   "back": "/lesson_one/introduction/page_six",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "Exercises", "user": request.session['user']})

def exercises_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/exercises/page_two.html", {"next": "/lesson_one/exercises/page_three",
                                                                   "back": "/lesson_one/exercises/page_one",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "Exercises", "user": request.session['user']})

def exercises_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/exercises/page_three.html", {"next": "/lesson_one/exercises/page_four",
                                                                     "back": "/lesson_one/exercises/page_two",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Unit 1: About Me", "title": "Exercises", "user": request.session['user']})

def exercises_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/exercises/page_four.html", {"next": "/lesson_one/exercises/page_five",
                                                                    "back": "/lesson_one/exercises/page_three",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "Exercises", "user": request.session['user']})

def exercises_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/exercises/page_five.html", {"next": "/lesson_one/exercises/page_six",
                                                                    "back": "/lesson_one/exercises/page_four",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "Exercises", "user": request.session['user']})

def exercises_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/exercises/page_six.html", {"next": "/lesson_one/exercises/page_seven",
                                                                   "back": "/lesson_one/exercises/page_five",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "Exercises", "user": request.session['user']})

def exercises_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/exercises/page_seven.html", {"next": "/lesson_one/character_select/page_one",
                                                                     "back": "/lesson_one/exercises/page_six",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Unit 1: About Me", "title": "Exercises", "user": request.session['user']})

def character_select_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/character_select/page_one.html", {"next": "/lesson_one/character_select/page_two",
                                                                          "back": "/lesson_one/exercises/page_seven",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user']})

def character_select_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/character_select/page_two.html", {"next": "/lesson_one/character_select/page_three",
                                                                          "back": "/lesson_one/character_select/page_one",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                                                                          "parts": {
                                                                              "body_color": "[id^=Koza]",
                                                                              "neck": "[id^=Vrat]"
                                                                          },
                                                                          "colors": {
                                                                              "body_color": request.session['body_color'],
                                                                              "neck": request.session['neck']
                                                                          }
                                                                          })

def character_select_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        parts = {}
        colors = {}
        if request.session['user']['sex'] == "M":
            src_ref = "svg/lesson1/male_avatar/body/glasses/" + request.session['height'] + "/" + request.session['body_type'] + "/short_hair/no_beard.svg"
        else:
            src_ref = "svg/lesson1/female_avatar/body/glasses/" + request.session['height'] + "/" + request.session['body_type'] + "/dress/long.svg"
        return render(request, "lesson1/character_select/page_three.html", {"next": "/lesson_one/character_select/page_four",
                                                                            "back": "/lesson_one/character_select/page_two",
                                                                            "lesson_one": lesson_one,
                                                                            "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                                                                            "src": src_ref,
                                                                            "parts": {
                                                                                "body_color": "[id^=Koza]",
                                                                                "neck": "[id^=Vrat]"
                                                                            },
                                                                            "colors": {
                                                                                "body_color": request.session['body_color'],
                                                                                "neck": request.session['neck']
                                                                            }
                                                                            })

def character_select_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            src_ref = "svg/lesson1/male_avatar/body/glasses/" + request.session['height'] + "/" + request.session['body_type'] + "/" + request.session['hair_type'] + "/no_beard.svg"
            if request.session['hair_type'] == "bald":
                colors = {
                    "body_color": request.session['body_color'],
                    "neck": request.session['neck']
                }
            else:
                colors = {
                    "body_color": request.session['body_color'],
                    "neck": request.session['neck'],
                    "hair_color": request.session['hair_color']
                }
        else:
            src_ref = "svg/lesson1/female_avatar/body/glasses/" + request.session['height'] + "/" + request.session['body_type'] + "/dress/" + request.session['hair_type'] + ".svg"
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color']
            }
        return render(request, "lesson1/character_select/page_four.html", {"next": "/lesson_one/character_select/page_five",
                                                                           "back": "/lesson_one/character_select/page_three",
                                                                           "lesson_one": lesson_one,
                                                                           "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                                                                           "src": src_ref,
                                                                           "parts": {
                                                                               "body_color": "[id^=Koza]",
                                                                               "neck": "[id^=Vrat]",
                                                                               "hair_color": "[id^=Lasje]",
                                                                           },
                                                                           "colors": colors
                                                                           })

def character_select_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        parts = {}
        if request.session['user']['sex'] == "M":
            src_ref = "svg/lesson1/male_avatar/body/" + request.session['glasses'] + "/" + request.session['height'] + "/" + request.session['body_type'] + "/" + request.session['hair_type'] + "/" \
                      + request.session['beard'] + ".svg"
            if request.session['beard'] == "full_beard":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "beard": "[id^=Brki],[id^=Brada]"
                }
            elif request.session['beard'] == "mustache" or request.session['beard'] == "goatee":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "beard": "[id^=Brki]"
                }
            elif request.session['beard'] == "no_beard":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                }
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color']
            }
            print(colors)
        else:
            src_ref = "svg/lesson1/female_avatar/body/" + request.session['glasses'] + "/" + request.session['height'] + "/" + request.session['body_type'] + "/dress/" + request.session[
                'hair_type'] + ".svg"
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color']
            }
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
            }
        return render(request, "lesson1/character_select/page_five.html", {"next": "/lesson_one/character_select/page_six",
                                                                           "back": "/lesson_one/character_select/page_four",
                                                                           "lesson_one": lesson_one,
                                                                           "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                                                                           "src": src_ref,
                                                                           "parts": parts,
                                                                           "colors": colors
                                                                           })

def character_select_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            src_ref = "svg/lesson1/male_avatar/head/" + request.session['glasses'] + "/" + request.session['hair_type'] + "/" + request.session['beard'] + ".svg"

            if request.session['beard'] == "full_beard":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "beard": "[id^=Brki],[id^=Brada]",
                    "Krog": "[id^=Krog]",
                    "Pulover": "[id^=Pulover]"
                }
            elif request.session['beard'] == "mustache" or request.session['beard'] == "goatee":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "beard": "[id^=Brki]",
                    "Krog": "[id^=Krog]",
                    "Pulover": "[id^=Pulover]"
                }
            elif request.session['beard'] == "no_beard":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "Krog": "[id^=Krog]",
                    "Pulover": "[id^=Pulover]"
                }
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color'],
                "suite_color": request.session['suite_color']
            }
        else:
            src_ref = "svg/lesson1/female/head/" + request.session['glasses'] + "/" + request.session['hair_type'] + ".svg"
            if request.session['wearing'] == "dress":
                colors = {
                    "body_color": request.session['body_color'],
                    "neck": request.session['neck'],
                    "hair_color": request.session['hair_color'],
                    "suite_color": request.session['dress_color']
                }
            else:
                colors = {
                    "body_color": request.session['body_color'],
                    "neck": request.session['neck'],
                    "hair_color": request.session['hair_color'],
                    "suite_color": request.session['shirt_color']
                }
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
                "shirt_color": "[id^=Majica]",
                "Krog": "[id^=Krog]",
            }
        return render(request, "lesson1/character_select/page_six.html", {"next": "/lesson_one/numbers/page_one",
                                                                          "back": "/lesson_one/character_select/page_five",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                                                                          "src": src_ref,
                                                                          "parts": parts,
                                                                          "colors": colors})

def numbers_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson_one/numbers/page_two",
                                                                 "back": "/lesson_one/character_select/page_six",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user'],
                                                                 "src": src_ref,
                                                                 "parts": parts,
                                                                 "colors": colors})

def numbers_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_two.html", {"next": "/lesson_one/numbers/page_three",
                                                                 "back": "/lesson_one/numbers/page_one",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_three.html", {"next": "/lesson_one/numbers/page_four",
                                                                   "back": "/lesson_one/numbers/page_two",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_four.html", {"next": "/lesson_one/numbers/page_five",
                                                                  "back": "/lesson_one/numbers/page_three",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_five.html", {"next": "/lesson_one/numbers/page_six",
                                                                  "back": "/lesson_one/numbers/page_four",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_six.html", {"next": "/lesson_one/numbers/page_seven",
                                                                 "back": "/lesson_one/numbers/page_five",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_seven.html", {"next": "/lesson_one/numbers/page_eight",
                                                                   "back": "/lesson_one/numbers/page_six",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_eight.html", {"next": "/lesson_one/numbers/page_nine",
                                                                   "back": "/lesson_one/numbers/page_seven",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_nine.html", {"next": "/lesson_one/numbers/page_ten",
                                                                  "back": "/lesson_one/numbers/page_seven",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_ten.html", {"next": "/lesson_one/numbers/page_eleven",
                                                                 "back": "/lesson_one/numbers/page_nine",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_eleven.html", {"next": "/lesson_one/numbers/page_twelve",
                                                                    "back": "/lesson_one/numbers/page_ten",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_twelve.html", {"next": "/lesson_one/numbers/page_thirteen",
                                                                    "back": "/lesson_one/numbers/page_eleven",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_thirteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_thirteen.html", {"next": "/lesson_one/numbers/page_fourteen",
                                                                      "back": "/lesson_one/numbers/page_twelve",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_fourteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_fourteen.html", {"next": "/lesson_one/numbers/page_fifteen",
                                                                      "back": "/lesson_one/numbers/page_thirteen",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_fifteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_fifteen.html", {"next": "/lesson_one/numbers/page_sixteen",
                                                                     "back": "/lesson_one/numbers/page_fourteen",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_sixteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_sixteen.html", {"next": "/lesson_one/numbers/page_seventeen",
                                                                     "back": "/lesson_one/numbers/page_fifteen",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_seventeen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_seventeen.html", {"next": "/lesson_one/numbers/page_eighteen",
                                                                       "back": "/lesson_one/numbers/page_sixteen",
                                                                       "lesson_one": lesson_one,
                                                                       "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_eighteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_eighteen.html", {"next": "/lesson_one/numbers/page_nineteen",
                                                                      "back": "/lesson_one/numbers/page_seventeen",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_nineteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_nineteen.html", {"next": "/lesson_one/numbers/page_twenty",
                                                                      "back": "/lesson_one/numbers/page_eighteen",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_twenty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_twenty.html", {"next": "/lesson_one/numbers/page_twentyone",
                                                                    "back": "/lesson_one/numbers/page_nineteen",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_twentyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_twentyone.html", {"next": "/lesson_one/numbers/page_twentytwo",
                                                                       "back": "/lesson_one/numbers/page_twenty",
                                                                       "lesson_one": lesson_one,
                                                                       "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_twentytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_twentytwo.html", {"next": "/lesson_one/colors/page_twentythree",
                                                                       "back": "/lesson_one/numbers/page_twentyone",
                                                                       "lesson_one": lesson_one,
                                                                       "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_twentythree(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_twentythree.html", {"next": "/lesson_one/colors/page_twentyfour",
                                                                         "back": "/lesson_one/numbers/page_twentytwo",
                                                                         "lesson_one": lesson_one,
                                                                         "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_twentyfour(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_twentyfour.html", {"next": "/lesson_one/numbers/page_twentyfive",
                                                                        "back": "/lesson_one/numbers/page_twentythree",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})

def numbers_page_twentyfive(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/numbers/page_twentyfive.html", {"next": "/lesson_one/colors/page_one",
                                                                        "back": "/lesson_one/numbers/page_twentyfour",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "Numbers", "user": request.session['user']})


def colors_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_one.html", {"next": "/lesson_one/colors/page_two",
                                                                "back": "/lesson_one/colors/page_twentyfive",
                                                                "lesson_one": lesson_one,
                                                                "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                "src": src_ref,
                                                                "parts": parts,
                                                                "colors": colors
                                                                })

def colors_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_two.html", {"next": "/lesson_one/colors/page_three",
                                                                "back": "/lesson_one/colors/page_one",
                                                                "lesson_one": lesson_one,
                                                                "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                "src": src_ref,
                                                                "parts": parts,
                                                                "colors": colors
                                                                })

def colors_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_three.html", {"next": "/lesson_one/colors/page_four",
                                                                  "back": "/lesson_one/colors/page_two",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })

def colors_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_four.html", {"next": "/lesson_one/colors/page_five",
                                                                 "back": "/lesson_one/colors/page_three",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                 "src": src_ref,
                                                                 "parts": parts,
                                                                 "colors": colors
                                                                 })

def colors_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_five.html", {"next": "/lesson_one/colors/page_six",
                                                                 "back": "/lesson_one/colors/page_four",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                 "src": src_ref,
                                                                 "parts": parts,
                                                                 "colors": colors
                                                                 })

def colors_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_six.html", {"next": "/lesson_one/colors/page_seven",
                                                                "back": "/lesson_one/colors/page_five",
                                                                "lesson_one": lesson_one,
                                                                "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                "src": src_ref,
                                                                "parts": parts,
                                                                "colors": colors
                                                                })

def colors_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_seven.html", {"next": "/lesson_one/colors/page_eight",
                                                                  "back": "/lesson_one/colors/page_six",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })

def colors_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_eight.html", {"next": "/lesson_one/colors/page_nine",
                                                                  "back": "/lesson_one/colors/page_seven",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })

def colors_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/colors/page_nine.html", {"next": "/lesson_one/years/page_one",
                                                                 "back": "/lesson_one/colors/page_eight",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Colours", "user": request.session['user'],
                                                                 "src": src_ref,
                                                                 "parts": parts,
                                                                 "colors": colors
                                                                 })

def years_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_one.html", {"next": "/lesson_one/years/page_two",
                                                               "back": "/lesson_one/colors/page_nine",
                                                               "lesson_one": lesson_one,
                                                               "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                               "src": src_ref,
                                                               "parts": parts,
                                                               "colors": colors
                                                               })

def years_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_two.html", {"next": "/lesson_one/years/page_three",
                                                               "back": "/lesson_one/years/page_one",
                                                               "lesson_one": lesson_one,
                                                               "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                               "src": src_ref,
                                                               "parts": parts,
                                                               "colors": colors
                                                               })

def years_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_three.html", {"next": "/lesson_one/years/page_four",
                                                                 "back": "/lesson_one/years/page_two",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                 "src": src_ref,
                                                                 "parts": parts,
                                                                 "colors": colors
                                                                 })

def years_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_four.html", {"next": "/lesson_one/years/page_five",
                                                                "back": "/lesson_one/years/page_three",
                                                                "lesson_one": lesson_one,
                                                                "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                "src": src_ref,
                                                                "parts": parts,
                                                                "colors": colors
                                                                })

def years_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_five.html", {"next": "/lesson_one/years/page_six",
                                                                "back": "/lesson_one/years/page_four",
                                                                "lesson_one": lesson_one,
                                                                "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                "src": src_ref,
                                                                "parts": parts,
                                                                "colors": colors
                                                                })

def years_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_six.html", {"next": "/lesson_one/years/page_seven",
                                                               "back": "/lesson_one/years/page_five",
                                                               "lesson_one": lesson_one,
                                                               "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                               "src": src_ref,
                                                               "parts": parts,
                                                               "colors": colors
                                                               })

def years_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_seven.html", {"next": "/lesson_one/years/page_eight",
                                                                 "back": "/lesson_one/years/page_six",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                 "src": src_ref,
                                                                 "parts": parts,
                                                                 "colors": colors
                                                                 })

def years_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_eight.html", {"next": "/lesson_one/years/page_nine",
                                                                 "back": "/lesson_one/years/page_seven",
                                                                 "lesson_one": lesson_one,
                                                                 "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                 "src": src_ref,
                                                                 "parts": parts,
                                                                 "colors": colors
                                                                 })

def years_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_nine.html", {"next": "/lesson_one/years/page_ten",
                                                                "back": "/lesson_one/years/page_eight",
                                                                "lesson_one": lesson_one,
                                                                "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                "src": src_ref,
                                                                "parts": parts,
                                                                "colors": colors
                                                                })

def years_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_ten.html", {"next": "/lesson_one/years/page_eleven",
                                                               "back": "/lesson_one/colors/page_eight",
                                                               "lesson_one": lesson_one,
                                                               "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                               "src": src_ref,
                                                               "parts": parts,
                                                               "colors": colors
                                                               })

def years_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_eleven.html", {"next": "/lesson_one/years/page_twelve",
                                                                  "back": "/lesson_one/colors/page_ten",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })

def years_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson1/years/page_twelve.html", {"next": "/lesson_one/personal_traits/page_one",
                                                                  "back": "/lesson_one/years/page_eleven",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 1: About Me", "title": "Years", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })

def personal_traits_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/personal_traits/page_one.html", {"next": "/lesson_one/personal_traits/page_two",
                                                                         "back": "/lesson_one/years/page_twelve",
                                                                         "lesson_one": lesson_one,
                                                                         "lesson": "Unit 1: About Me", "title": "Personal Traits", "user": request.session['user']})

def personal_traits_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/personal_traits/page_two.html", {"next": "/lesson_one/personal_traits/page_three",
                                                                         "back": "/lesson_one/personal_traits/page_one",
                                                                         "lesson_one": lesson_one,
                                                                         "lesson": "Unit 1: About Me", "title": "Personal Traits", "user": request.session['user']})

def personal_traits_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/personal_traits/page_three.html", {"next": "/lesson_one/personal_traits/page_four",
                                                                           "back": "/lesson_one/personal_traits/page_two",
                                                                           "lesson_one": lesson_one,
                                                                           "lesson": "Unit 1: About Me", "title": "Personal Traits", "user": request.session['user']})

def personal_traits_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/personal_traits/page_four.html", {"next": "/lesson_one/personal_traits/page_five",
                                                                          "back": "/lesson_one/personal_traits/page_three",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Unit 1: About Me", "title": "Personal Traits", "user": request.session['user']})

def personal_traits_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/personal_traits/page_five.html", {"next": "/lesson_one/personal_traits/page_six",
                                                                          "back": "/lesson_one/personal_traits/page_four",
                                                                          "lesson_one": lesson_one,
                                                                          "lesson": "Unit 1: About Me", "title": "Personal Traits", "user": request.session['user']})

def personal_traits_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/personal_traits/page_six.html", {"next": "/lesson_one/personal_traits/page_seven",
                                                                         "back": "/lesson_one/personal_traits/page_five",
                                                                         "lesson_one": lesson_one,
                                                                         "lesson": "Unit 1: About Me", "title": "Personal Traits", "user": request.session['user']})

def personal_traits_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/personal_traits/page_seven.html", {"next": "/lesson_one/personal_traits/page_eight",
                                                                           "back": "/lesson_one/personal_traits/page_six",
                                                                           "lesson_one": lesson_one,
                                                                           "lesson": "Unit 1: About Me", "title": "Personal Traits", "user": request.session['user']})

def he_she_it_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_one.html", {"next": "/lesson_one/he_she_it/page_two",
                                                                   "back": "/lesson_one/personal_traits/page_seven",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_two.html", {"next": "/lesson_one/he_she_it/page_three",
                                                                   "back": "/lesson_one/he_she_it/page_one",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_three.html", {"next": "/lesson_one/he_she_it/page_four",
                                                                     "back": "/lesson_one/he_she_it/page_two",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_four.html", {"next": "/lesson_one/he_she_it/page_five",
                                                                    "back": "/lesson_one/he_she_it/page_three",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_five.html", {"next": "/lesson_one/he_she_it/page_six",
                                                                    "back": "/lesson_one/he_she_it/page_four",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_six.html", {"next": "/lesson_one/he_she_it/page_seven",
                                                                   "back": "/lesson_one/he_she_it/page_five",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_seven.html", {"next": "/lesson_one/he_she_it/page_eight",
                                                                     "back": "/lesson_one/he_she_it/page_six",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_eight.html", {"next": "/lesson_one/he_she_it/page_nine",
                                                                     "back": "/lesson_one/he_she_it/page_seven",
                                                                     "lesson_one": lesson_one,
                                                                     "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_nine.html", {"next": "/lesson_one/he_she_it/page_ten",
                                                                    "back": "/lesson_one/he_she_it/page_eight",
                                                                    "lesson_one": lesson_one,
                                                                    "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_ten.html", {"next": "/lesson_one/he_she_it/page_eleven",
                                                                   "back": "/lesson_one/he_she_it/page_nine",
                                                                   "lesson_one": lesson_one,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_eleven.html", {"next": "/lesson_one/he_she_it/page_twelve",
                                                                      "back": "/lesson_one/he_she_it/page_ten",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twelve.html", {"next": "/lesson_one/he_she_it/page_thirteen",
                                                                      "back": "/lesson_one/he_she_it/page_eleven",
                                                                      "lesson_one": lesson_one,
                                                                      "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirteen.html", {"next": "/lesson_one/he_she_it/page_fourteen",
                                                                        "back": "/lesson_one/he_she_it/page_twelve",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_fourteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_fourteen.html", {"next": "/lesson_one/he_she_it/page_fifteen",
                                                                        "back": "/lesson_one/he_she_it/page_thirteen",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})


def he_she_it_page_fifteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_fifteen.html", {"next": "/lesson_one/he_she_it/page_sixteen",
                                                                        "back": "/lesson_one/he_she_it/page_fourteen",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_sixteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_sixteen.html", {"next": "/lesson_one/he_she_it/page_seventeen",
                                                                        "back": "/lesson_one/he_she_it/page_fifteen",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_seventeen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_seventeen.html", {"next": "/lesson_one/he_she_it/page_eighteen",
                                                                        "back": "/lesson_one/he_she_it/page_sixteen",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_eighteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_eighteen.html", {"next": "/lesson_one/he_she_it/page_nineteen",
                                                                        "back": "/lesson_one/he_she_it/page_seventeen",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_nineteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_nineteen.html", {"next": "/lesson_one/he_she_it/page_twenty",
                                                                        "back": "/lesson_one/he_she_it/page_eighteen",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twenty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twenty.html", {"next": "/lesson_one/he_she_it/page_twentyone",
                                                                        "back": "/lesson_one/he_she_it/page_nineteen",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentyone.html", {"next": "/lesson_one/he_she_it/page_twentytwo",
                                                                        "back": "/lesson_one/he_she_it/page_twenty",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentytwo.html", {"next": "/lesson_one/he_she_it/page_twentythree",
                                                                        "back": "/lesson_one/he_she_it/page_twentyone",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentythree(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentythree.html", {"next": "/lesson_one/he_she_it/page_twentyfour",
                                                                        "back": "/lesson_one/he_she_it/page_twentytwo",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentyfour(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentyfour.html", {"next": "/lesson_one/he_she_it/page_twentyfive",
                                                                        "back": "/lesson_one/he_she_it/page_twentythree",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentyfive(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentyfive.html", {"next": "/lesson_one/he_she_it/page_twentysix",
                                                                        "back": "/lesson_one/he_she_it/page_twentyfour",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentysix(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentysix.html", {"next": "/lesson_one/he_she_it/page_twentyseven",
                                                                        "back": "/lesson_one/he_she_it/page_twentyfive",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentyseven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentyseven.html", {"next": "/lesson_one/he_she_it/page_twentyeight",
                                                                        "back": "/lesson_one/he_she_it/page_twentysix",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentyeight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentyeight.html", {"next": "/lesson_one/he_she_it/page_twentynine",
                                                                        "back": "/lesson_one/he_she_it/page_twentyseven",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_twentynine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_twentynine.html", {"next": "/lesson_one/he_she_it/page_thirty",
                                                                        "back": "/lesson_one/he_she_it/page_twentyeight",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirty.html", {"next": "/lesson_one/he_she_it/page_thirtyone",
                                                                        "back": "/lesson_one/he_she_it/page_twentynine",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtyone.html", {"next": "/lesson_one/he_she_it/page_thirtytwo",
                                                                        "back": "/lesson_one/he_she_it/page_thirty",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtytwo.html", {"next": "/lesson_one/he_she_it/page_thirtythree",
                                                                        "back": "/lesson_one/he_she_it/page_thirtyone",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtythree(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtythree.html", {"next": "/lesson_one/he_she_it/page_thirtyfour",
                                                                        "back": "/lesson_one/he_she_it/page_thirtytwo",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtyfour(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtyfour.html", {"next": "/lesson_one/he_she_it/page_thirtyfive",
                                                                        "back": "/lesson_one/he_she_it/page_thirtythree",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtyfive(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtyfive.html", {"next": "/lesson_one/he_she_it/page_thirtysix",
                                                                        "back": "/lesson_one/he_she_it/page_thirtyfour",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtysix(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtysix.html", {"next": "/lesson_one/he_she_it/page_thirtyseven",
                                                                        "back": "/lesson_one/he_she_it/page_thirtyfive",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtyseven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtyseven.html", {"next": "/lesson_one/he_she_it/page_thirtyeight",
                                                                        "back": "/lesson_one/he_she_it/page_thirtysix",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtyeight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtyeight.html", {"next": "/lesson_one/he_she_it/page_thirtynine",
                                                                        "back": "/lesson_one/he_she_it/page_thirtyseven",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_thirtynine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_thirtynine.html", {"next": "/lesson_one/he_she_it/page_forty",
                                                                        "back": "/lesson_one/he_she_it/page_thirtyeight",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_forty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_forty.html", {"next": "/lesson_one/he_she_it/page_fortyone",
                                                                        "back": "/lesson_one/he_she_it/page_thirtynine",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_fortyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_fortyone.html", {"next": "/lesson_one/he_she_it/page_fortytwo",
                                                                        "back": "/lesson_one/he_she_it/page_forty",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})

def he_she_it_page_fortytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if 'user' not in request.session:
            return login_page(request)
        return render(request, "lesson1/he_she_it/page_fortytwo.html", {"next": "/lesson_two",
                                                                        "back": "/lesson_one/he_she_it/page_fortyone",
                                                                        "lesson_one": lesson_one,
                                                                        "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user']})


#Unit3
def lesson_three_title(request):
    if request.method == "GET":
        return render(request, "lesson3/title_page.html", {"next": "lesson_three/pronouns/page_one", "back": "/", "lesson_one": lesson_one,
                                                                      "lesson": "Unit 3: Let's Eat", "title": "", "user": request.session['user']})



def pronouns_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson3/pronouns/page_one.html", {"next": "/lesson_three/pronouns/page_two",
                                                                  "back": "/lesson_three/title",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })


def pronouns_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson3/pronouns/page_two.html", {"next": "/lesson_three/pronouns/page_three",
                                                                  "back": "/lesson_three/pronouns/page_one",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })


def pronouns_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson3/pronouns/page_three.html", {"next": "/lesson_three/pronouns/page_four",
                                                                  "back": "/lesson_three/pronouns/page_two",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })


def pronouns_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson3/pronouns/page_four.html", {"next": "/lesson_three/pronouns/page_five",
                                                                  "back": "/lesson_three/pronouns/page_three",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })


def pronouns_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson3/pronouns/page_five.html", {"next": "/lesson_three/pronouns/page_six",
                                                                  "back": "/lesson_three/pronouns/page_four",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })


def pronouns_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        if request.session['user']['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=User.objects.get(email=request.session['user']['email']))
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.filter(user=request.session['user'])
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + ".svg"
        return render(request, "lesson3/pronouns/page_six.html", {"next": "/lesson_three/pronouns/page_six",
                                                                  "back": "/lesson_three/pronouns/page_five",
                                                                  "lesson_one": lesson_one,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns", "user": request.session['user'],
                                                                  "src": src_ref,
                                                                  "parts": parts,
                                                                  "colors": colors
                                                                  })