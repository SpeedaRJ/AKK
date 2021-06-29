import os
import re

from django.http import HttpResponseNotAllowed, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from ucbenik.CustomAuth import CustomAuth
from ucbenik.models import User, CharacterDataMen, CharacterDataWomen, Solution
from .serializers import UserSerializer

lessons = {"lesson_one": {"Introduction": "/lesson_one/introduction/page_one",
                          "Appearance": "/lesson_one/character_select/page_one",
                          "Numbers": "/lesson_one/numbers/page_one",
                          "Colours": "/lesson_one/colors/page_one",
                          "Years": "/lesson_one/years/page_one",
                          "Personality Traits": "/lesson_one/personal_traits/page_one",
                          "He, She, It": "/lesson_one/he_she_it/page_one"},
           "lesson_two": {"Day Week Month": "/lesson_two/day_week_month/page_one",
                          "Articles": "/lesson_two/articles/page_one",
                          "Family Members": "/lesson_two/family/page_one",
                          "Clothes": "/lesson_two/clothes/page_one",
                          "Time": "/lesson_two/time/page_one",
                          "Present Simple": "/lesson_two/present_simple/page_one",
                          "Daily Routines": "/lesson_two/daily_routines/page_one",
                          "Occupations": "/lesson_two/occupations/page_one"},
           "lesson_three": {"Pronouns": "/lesson_three/pronouns/page_one",
                            "Modal Verbs": "/lesson_three/modal_verbs/page_one"}
           }


def save_avatar(session):
    user = User.objects.get(email=session['user']['email'])
    if user.sex == 'F':
        avatar = CharacterDataWomen(user=user, glasses=session['glasses'], hair_type=session['hair_type'],
                                    body_type=session['body_type'])
    else:
        avatar = CharacterDataMen(user=user, glasses=session['glasses'], hair_type=session['hair_type'],
                                  beard=session['beard'], body_type=session['body_type'])
    avatar.save()


def get_user_avatar(user_dict):
    user = User.objects.get(email=user_dict['email'])
    try:
        if user_dict['sex'] == "M":
            data_set = CharacterDataMen.objects.get(user=user)
            src_ref = "svg/lesson1/male_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + "/" + data_set.beard + ".svg"
            parts, colors = getColorsAndParts(data_set, "M")
        else:
            data_set = CharacterDataWomen.objects.get(user=user)
            parts, colors = getColorsAndParts(data_set, "W")
            src_ref = "svg/lesson1/female_avatar/head/" + data_set.glasses + "/" + data_set.hair_type + ".svg"
    except:
        parts = {}
        colors = {}
        src_ref = ""
    return (src_ref, parts, colors)


def get_or_create_solution(user, link):
    try:
        solution = Solution.objects.get(user=user, link=link)
    except Solution.DoesNotExist:
        solution = Solution(user=user, link=link, solved=False)
        solution.save()
    return solution


def save_solution(user, link):
    try:
        solution = Solution.objects.get(user=user, link=link)
        solution.solve()
        return True
    except Solution.DoesNotExist:
        return False


def get_refferer(request):
    if 'last_page' not in request.session or request.path == request.session['last_page']:
        return True
    if 'HTTP_REFERER' not in request.META:
        return False
    return True


def coming_soon(request):
    back = re.sub(r'[^/]*//[^/]*', '', request.META['HTTP_REFERER'])
    if 'avatar' in request.session:
        src_ref = request.session['avatar']['src_ref']
        parts = request.session['avatar']['parts']
        colors = request.session['avatar']['colors']
    else:
        src_ref, parts, colors = get_user_avatar(request.session['user'])
        request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
    return render(request, "comming_soon.html", {"next": "/", "back": back,
                                                 "lessons": lessons,
                                                 "lesson": "Coming Soon", "title": "Coming Soon",
                                                 "user": request.session['user'],
                                                 "src": src_ref, "parts": parts, "colors": colors})


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
                       'name': first_name,
                       'age': age,
                       'sex': sex
                       }
            return render(request, 'register.html', context)
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
        try:
            user = user_check.authenticate(request, username, password)
            request.session.flush()
            request.session['user'] = UserSerializer(user).data
            if user.last_page:
                return redirect(user.last_page)
            else:
                return redirect('/')
        except:
            try:
                User.objects.get(email=username)
                context = {'no_user': 'Napačno geslo',
                           'username': username}
                return render(request, "login.html", context)
            except User.DoesNotExist:
                context = {'no_user': 'Vaš uporabniški račun še ne obstaja.Najprej se registrirajte.',
                           'username': username}
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
    # for key, value in request.session.items():
    #    print('{} => {}'.format(key, value))
    return HttpResponse('ok')


def save_session(request):
    user = User.objects.get_by_natural_key(request.session['user']['email'])
    if request.session['user']['sex'] == "M":
        cs = CharacterDataMen(
            user=user,
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
        if 'neck' in request.session:
            neck = request.session['neck']
        else:
            neck = ''
        if 'body_color' in request.session:
            body_color = request.session['body_color']
        else:
            body_color = ''
        if 'height' in request.session:
            height = request.session['height']
        else:
            height = 'short'
        if 'body_type' in request.session:
            body_type = request.session['body_type']
        else:
            body_type = ''
        if 'hair_color' in request.session:
            hc = request.session['hair_color']
        else:
            hc = ''
        if 'glasses' in request.session:
            glasses = request.session['glasses']
        else:
            glasses = 'glasses'
        if 'shoes_color' in request.session:
            sc = request.session['shoes_color']
        else:
            sc = ''
        if 'pants_color' in request.session:
            pc = request.session['pants_color']
        else:
            pc = ''
        if 'shirt_color' in request.session:
            shirt_color = request.session['shirt_color']
        else:
            shirt_color = ''
        if 'hair_type' in request.session:
            hair_type = request.session['hair_type']
        else:
            hair_type = 'curly'
        if 'wearing' in request.session:
            wearing = request.session['wearing']
        else:
            wearing = 'dress'
        if 'dress_color' in request.session:
            dress_color = request.session['dress_color']
        else:
            dress_color = "#0474bb"
        cs = CharacterDataWomen(
            user=user,
            neck=neck,
            body_color=body_color,
            height=height,
            body_type=body_type,
            hair_color=hc,
            glasses=glasses,
            shoes_color=sc,
            pants_color=pc,
            shirt_color=shirt_color,
            hair_type=hair_type,
            wearing=wearing,
            dress_color=dress_color,
        )
    try:
        cs.save()
        return HttpResponse('ok')
    except NameError:
        print(f"AVATAR NOT SAVED\n{NameError}")
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
                "Pulover": "[id^=Pulover]",
                "Obrv1": "[id^=Obrve]"
            }
        elif data_set.beard == "full_beard" or "mustache" or data_set.beard == "goatee":
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
                "beard": "[id^=Brki]",
                "Krog": "[id^=Krog]",
                "Pulover": "[id^=Pulover]",
                "Obrv1": "[id^=Obrve]"
            }
        elif data_set.beard == "no_beard":
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
                "Krog": "[id^=Krog]",
                "Pulover": "[id^=Pulover]",
                "Obrv1": "[id^=Obrve]"
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
            "Obrv1": "[id^=Obrve]"
        }
        return parts, colors


# UNIT 1

def lesson_one_title(request):
    if request.method == "GET":
        return render(request, "lesson1/title_page.html", {"next": "/lesson_one/introduction/page_one", "back": "/",
                                                           "lessons": lessons,
                                                           "lesson": "Unit 1: About Me", "title": "",
                                                           "user": request.session['user']})


def introduction_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        solution = get_or_create_solution(user, request.path)
        user.add_chapter('Introduction')
        request.session['user'] = UserSerializer(user).data
        return render(request, "lesson1/introduction/page_one.html",
                      {"next": "/lesson_one/introduction/page_two", "back": "/", "solved": solution.solved,
                       "lessons": lessons,
                       "solved": solution.solved,
                       "lesson": "Unit 1: About Me", "title": "Introduction", "user": request.session['user']})


def introduction_page_two(request):
    back = "/lesson_one/introduction/page_one"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/introduction/page_two.html", {"next": "/lesson_one/introduction/page_three",
                                                                      "back": back, "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me",
                                                                      "title": "Introduction",
                                                                      "user": request.session['user']})


def introduction_page_three(request):
    back = "/lesson_one/introduction/page_two"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/introduction/page_three.html", {"next": "/lesson_one/introduction/page_four",
                                                                        "back": back, "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "Introduction",
                                                                        "user": request.session['user']})


def introduction_page_four(request):
    back = "/lesson_one/introduction/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/introduction/page_four.html", {"next": "/lesson_one/introduction/page_five",
                                                                       "back": back, "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 1: About Me",
                                                                       "title": "Introduction",
                                                                       "user": request.session['user']})


def introduction_page_five(request):
    back = "/lesson_one/introduction/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/introduction/page_five.html", {"next": "/lesson_one/introduction/page_six",
                                                                       "back": back, "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 1: About Me",
                                                                       "title": "Introduction",
                                                                       "user": request.session['user']})


def introduction_page_six(request):
    back = "/lesson_one/introduction/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/introduction/page_six.html", {"next": "/lesson_one/introduction/page_seven",
                                                                      "back": back,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me",
                                                                      "title": "Introduction",
                                                                      "user": request.session['user']})


def introduction_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        return render(request, "lesson1/introduction/page_seven.html", {"next": "/lesson_one/introduction/page_eight",
                                                                        "back": "/lesson_one/introduction/page_six",
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "Introduction",
                                                                        "user": request.session['user']})


def introduction_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        return render(request, "lesson1/introduction/page_eight.html", {"next": "/lesson_one/exercises/page_one",
                                                                        "back": "/lesson_one/introduction/page_seven",
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "Introduction",
                                                                        "user": request.session['user']})


def exercises_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/exercises/page_one.html", {"next": "/lesson_one/exercises/page_two",
                                                                   "back": "/lesson_one/introduction/page_seven",
                                                                   "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "Exercises",
                                                                   "user": request.session['user']})


def exercises_page_two(request):
    back = "/lesson_one/exercises/page_one"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/exercises/page_two.html", {"next": "/lesson_one/exercises/page_three",
                                                                   "back": back, "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "Exercises",
                                                                   "user": request.session['user']})


def exercises_page_three(request):
    back = "/lesson_one/exercises/page_two"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/exercises/page_three.html", {"next": "/lesson_one/exercises/page_four",
                                                                     "back": back, "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "Exercises",
                                                                     "user": request.session['user']})


def exercises_page_four(request):
    back = "/lesson_one/exercises/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/exercises/page_four.html", {"next": "/lesson_one/exercises/page_five",
                                                                    "back": back,
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "Exercises",
                                                                    "user": request.session['user']})


def exercises_page_five(request):
    back = "/lesson_one/exercises/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/exercises/page_five.html", {"next": "/lesson_one/exercises/page_six",
                                                                    "back": back,
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "Exercises",
                                                                    "user": request.session['user']})


def exercises_page_six(request):
    back = "/lesson_one/exercises/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/exercises/page_six.html", {"next": "/lesson_one/exercises/page_seven",
                                                                   "back": back,
                                                                   "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "Exercises",
                                                                   "user": request.session['user']})


def exercises_page_seven(request):
    back = "/lesson_one/exercises/page_six"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/exercises/page_seven.html", {"next": "/lesson_one/character_select/page_one",
                                                                     "back": back,
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "Exercises",
                                                                     "user": request.session['user']})


def character_select_page_one(request):
    back = "/lesson_one/exercises/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        user = user
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter('Appearance')
        request.session['user'] = UserSerializer(user).data
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/character_select/page_one.html",
                      {"next": "/lesson_one/character_select/page_two",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user']})


def character_select_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'neck' in request.session:
            neck = request.session['neck']
        else:
            return redirect('/lesson_one/character_select/page_one')
        if 'body_color' in request.session:
            body_color = request.session['body_color']
        else:
            return redirect('/lesson_one/character_select/page_one')
        return render(request, "lesson1/character_select/page_two.html",
                      {"next": "/lesson_one/character_select/page_three",
                       "back": "/lesson_one/character_select/page_one",
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                       "parts": {
                           "body_color": "[id^=Koza]",
                           "neck": "[id^=Vrat]"
                       },
                       "colors": {
                           "body_color": body_color,
                           "neck": neck
                       }})


def character_select_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        parts = {}
        colors = {}
        if 'hair_color' in request.session:
            hair_color = request.session['hair_color']
        else:
            hair_color = '#ffebc6'
        if 'height' in request.session:
            height = request.session['height']
        else:
            height = "short"
            request.session['height'] = 'short'
        if 'body_type' in request.session:
            body_type = request.session['body_type']
        else:
            body_type = 'slim'
            request.session['body_type'] = 'slim'
        if 'neck' in request.session:
            neck = request.session['neck']
        else:
            return redirect('/lesson_one/character_select/page_one')
        if 'body_color' in request.session:
            body_color = request.session['body_color']
        else:
            return redirect('/lesson_one/character_select/page_one')
        if request.session['user']['sex'] == "M":
            if 'hair_type' in request.session:
                hair_type = request.session['hair_type']
            else:
                hair_type = 'short_hair'
            src_ref = f"svg/lesson1/male_avatar/body/glasses/{height}/{body_type}/{hair_type}/no_beard.svg"
        else:
            if 'hair_type' in request.session:
                hair_type = request.session['hair_type']
            else:
                hair_type = 'long'
            src_ref = f"svg/lesson1/female_avatar/body/glasses/{height}/{body_type}/dress/{hair_type}.svg"
        return render(request, "lesson1/character_select/page_three.html",
                      {"next": "/lesson_one/character_select/page_four",
                       "back": "/lesson_one/character_select/page_two",
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                       "src": src_ref,
                       "parts": {
                           "body_color": "[id^=Koza]",
                           "neck": "[id^=Vrat]"
                       },
                       "colors": {
                           "body_color": body_color,
                           "neck": neck
                       },
                       "hair_type": hair_type,
                       "hair_color": hair_color})


def character_select_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'hair_color' in request.session:
            hair_color = request.session['hair_color']
        else:
            return redirect('/lesson_one/character_select/page_three')
        if 'height' in request.session:
            height = request.session['height']
        else:
            height = 'short'
            request.session['height'] = height
        if 'body_type' in request.session:
            body_type = request.session['body_type']
        else:
            body_type = 'slim'
            request.session['body_type'] = 'slim'
        if 'hair_type' in request.session:
            hair_type = request.session['hair_type']
        else:
            return redirect('/lesson_one/character_select/page_three')
        if 'glasses' in request.session:
            glasses = request.session['glasses']
        else:
            glasses = 'glasses'
        if 'beard' in request.session:
            beard = request.session['beard']
        else:
            beard = 'no_beard'
        if request.session['user']['sex'] == "M":
            src_ref = f"svg/lesson1/male_avatar/body/{glasses}/{height}/{body_type}/{hair_type}/{beard}.svg"
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color']
            }
        else:
            src_ref = f"svg/lesson1/female_avatar/body/{glasses}/{height}/{body_type}/dress/{hair_type}.svg"
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color']
            }
        return render(request, "lesson1/character_select/page_four.html",
                      {"next": "/lesson_one/character_select/page_five",
                       "back": "/lesson_one/character_select/page_three",
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                       "src": src_ref,
                       "parts": {
                           "body_color": "[id^=Koza]",
                           "neck": "[id^=Vrat]",
                           "hair_color": "[id^=Lasje]",
                           "Obrv1": "[id^=Obrve]",
                           "beard": "[id^=Brada]",
                           "mustache": "[id^=Brki]",
                       },
                       "colors": colors
                       })


def character_select_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        parts = {}
        if 'height' in request.session:
            height = request.session['height']
        else:
            return redirect('/lesson_one/character_select/page_one')
        if 'body_type' in request.session:
            body_type = request.session['body_type']
        else:
            body_type = 'slim'
            request.session['body_type'] = 'slim'
        if 'hair_type' in request.session:
            hair_type = request.session['hair_type']
        else:
            return redirect('/lesson_one/character_select/page_three')
        if 'glasses' in request.session:
            glasses = request.session['glasses']
        else:
            glasses = 'glasses'
        if 'beard' in request.session:
            beard = request.session['beard']
        else:
            beard = 'no_beard'
            request.session['beard'] = beard
        if request.session['user']['sex'] == "M":
            src_ref = f"svg/lesson1/male_avatar/body/{glasses}/{height}/{body_type}/{hair_type}/{beard}.svg"
            if request.session['beard'] == "full_beard":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "beard": "[id^=Brki],[id^=Brada]",
                    "Obrv1": "[id^=Obrve]",
                }
            elif request.session['beard'] == "mustache" or request.session['beard'] == "goatee":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "beard": "[id^=Brki]",
                    "Obrv1": "[id^=Obrve]",
                }
            elif request.session['beard'] == "no_beard":
                parts = {
                    "body_color": "[id^=Koza]",
                    "neck": "[id^=Vrat]",
                    "hair_color": "[id^=Lasje]",
                    "Obrv1": "[id^=Obrve]",
                }
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color']
            }
        else:
            wearing = request.GET.get('wearing')
            if not wearing:
                wearing = "dress"
            src_ref = f"svg/lesson1/female_avatar/body/{glasses}/{height}/{body_type}/{wearing}/{hair_type}.svg"
            colors = {
                "body_color": request.session['body_color'],
                "neck": request.session['neck'],
                "hair_color": request.session['hair_color'],
                "shoes_color": request.GET.get('shoes_color')
            }
            request.session["shoes_color"] = f"#{request.GET.get('shoes_color')}"
            parts = {
                "body_color": "[id^=Koza]",
                "neck": "[id^=Vrat]",
                "hair_color": "[id^=Lasje]",
                "shoe1": "[id^=cevlje]",
                "shoe2": "[id^=cevlje-2]"
            }
            if wearing == 'dress':
                colors["dress_color"] = request.GET.get('dress_color')
                request.session["dress_color"] = request.GET.get('dress_color')
                parts["dress"] = "[id^=Obleka]"
            else:
                colors["pants_color"] = request.GET.get('pants_color')
                request.session["pants_color"] = request.GET.get('pants_color')
                colors["shirt_color"] = request.GET.get('shirt_color')
                request.session["shirt_color"] = request.GET.get('shirt_color')
                parts["shirt"] = "[id^=Majica]"
                parts["pants"] = "[id^=Hlace]"
        return render(request, "lesson1/character_select/page_five.html",
                      {"next": "/lesson_one/character_select/page_six",
                       "back": "/lesson_one/character_select/page_four",
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Avatar", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def character_select_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        user = request.session['user']
        try:
            src_ref, parts, colors = get_user_avatar(user)
        except:
            return redirect("/lesson_one/character_select/page_one")
        request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/character_select/page_six.html", {"next": "/lesson_one/numbers/page_one",
                                                                          "back": "/lesson_one/character_select/page_five",
                                                                          "lessons": lessons,
                                                                          "lesson": "Unit 1: About Me",
                                                                          "title": "Avatar", "user": user,
                                                                          "src": src_ref, "parts": parts,
                                                                          "colors": colors})


# NUMBERS

def numbers_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        user = user
        user.add_chapter('Numbers')
        request.session['user'] = UserSerializer(user).data
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_one.html", {"next": "/lesson_one/numbers/page_two",
                                                                 "back": "/lesson_one/character_select/page_six",
                                                                 "lessons": lessons, "solved": solution.solved,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_two(request):
    back = "/lesson_one/numbers/page_one"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/numbers/page_two.html", {"next": "/lesson_one/numbers/page_three",
                                                                 "back": back,
                                                                 "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_three(request):
    back = "/lesson_one/numbers/page_two"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_three.html", {"next": "/lesson_one/numbers/page_four",
                                                                   "back": back, "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_four(request):
    back = "/lesson_one/numbers/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_four.html", {"next": "/lesson_one/numbers/page_five",
                                                                  "back": back, "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_five(request):
    back = "/lesson_one/numbers/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_five.html", {"next": "/lesson_one/numbers/page_six",
                                                                  "back": back, "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_six(request):
    back = "/lesson_one/numbers/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_six.html", {"next": "/lesson_one/numbers/page_seven",
                                                                 "back": back,
                                                                 "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_seven(request):
    back = "/lesson_one/numbers/page_six"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_seven.html", {"next": "/lesson_one/numbers/page_eight",
                                                                   "back": back, "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_eight(request):
    back = "/lesson_one/numbers/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_eight.html", {"next": "/lesson_one/numbers/page_nine",
                                                                   "back": back, "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_nine(request):
    back = "/lesson_one/numbers/page_eight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_nine.html", {"next": "/lesson_one/numbers/page_ten",
                                                                  "back": back, "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_ten(request):
    back = "/lesson_one/numbers/page_nine"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/numbers/page_ten.html", {"next": "/lesson_one/numbers/page_eleven",
                                                                 "back": back,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_eleven(request):
    back = "/lesson_one/numbers/page_ten"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/numbers/page_eleven.html", {"next": "/lesson_one/numbers/page_twelve",
                                                                    "back": back,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_twelve.html", {"next": "/lesson_one/numbers/page_thirteen",
                                                                    "back": "/lesson_one/numbers/page_eleven",
                                                                    "solved": solution.solved, "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_thirteen(request):
    back = "/lesson_one/numbers/page_twelve"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/numbers/page_thirteen.html", {"next": "/lesson_one/numbers/page_fourteen",
                                                                      "back": back, "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_fourteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/numbers/page_fourteen.html", {"next": "/lesson_one/numbers/page_fifteen",
                                                                      "back": "/lesson_one/numbers/page_thirteen",
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_fifteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/numbers/page_fifteen.html", {"next": "/lesson_one/numbers/page_sixteen",
                                                                     "back": "/lesson_one/numbers/page_fourteen",
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_sixteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/numbers/page_sixteen.html", {"next": "/lesson_one/numbers/page_seventeen",
                                                                     "back": "/lesson_one/numbers/page_fifteen",
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_seventeen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/numbers/page_seventeen.html", {"next": "/lesson_one/numbers/page_eighteen",
                                                                       "back": "/lesson_one/numbers/page_sixteen",
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts,
                                                                       "colors": colors})


def numbers_page_eighteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/numbers/page_eighteen.html", {"next": "/lesson_one/numbers/page_nineteen",
                                                                      "back": "/lesson_one/numbers/page_seventeen",
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_nineteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_nineteen.html", {"next": "/lesson_one/numbers/page_twenty",
                                                                      "back": "/lesson_one/numbers/page_eighteen",
                                                                      "solved": solution.solved, "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_twenty(request):
    back = "/lesson_one/numbers/page_nineteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_twenty.html", {"next": "/lesson_one/numbers/page_twentyone",
                                                                    "back": back, "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors})


def numbers_page_twentyone(request):
    back = "/lesson_one/numbers/page_twenty"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/numbers/page_twentyone.html", {"next": "/lesson_one/numbers/page_twentytwo",
                                                                       "back": back, "lessons": lessons,
                                                                       "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts,
                                                                       "colors": colors})


def numbers_page_twentytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/numbers/page_twentytwo.html", {"next": "/lesson_one/numbers/page_twentythree",
                                                                       "back": "/lesson_one/numbers/page_twentyone",
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 1: About Me", "title": "Numbers",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts,
                                                                       "colors": colors})


def numbers_page_twentythree(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_twentythree.html", {"next": "/lesson_one/numbers/page_twentyfour",
                                                                         "back": "/lesson_one/numbers/page_twentytwo",
                                                                         "solved": solution.solved,
                                                                         "lessons": lessons,
                                                                         "lesson": "Unit 1: About Me",
                                                                         "title": "Numbers",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors})


def numbers_page_twentyfour(request):
    back = "/lesson_one/numbers/page_twentythree"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_twentyfour.html", {"next": "/lesson_one/numbers/page_twentyfive",
                                                                        "back": back, "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "Numbers",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


def numbers_page_twentyfive(request):
    back = "/lesson_one/numbers/page_twentyfour"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/numbers/page_twentyfive.html", {"next": "/lesson_one/colors/page_one",
                                                                        "back": back, "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "Numbers",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


# COLORS
def colors_page_one(request):
    back = "/lesson_one/numbers/page_twentyfive"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        user = user
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter('Colours')
        request.session['user'] = UserSerializer(user).data
        return render(request, "lesson1/colors/page_one.html", {"next": "/lesson_one/colors/page_two",
                                                                "back": back,
                                                                "lessons": lessons,
                                                                "lesson": "Unit 1: About Me", "title": "Colours",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def colors_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/colors/page_two.html", {"next": "/lesson_one/colors/page_three",
                                                                "back": "/lesson_one/colors/page_one",
                                                                "lessons": lessons,
                                                                "lesson": "Unit 1: About Me", "title": "Colours",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def colors_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/colors/page_three.html", {"next": "/lesson_one/colors/page_four",
                                                                  "back": "/lesson_one/colors/page_two",
                                                                  "solved": solution.solved, "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Colours",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def colors_page_four(request):
    back = "/lesson_one/colors/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(User.objects.get(email=request.session['user']['email']), request.path)
        return render(request, "lesson1/colors/page_four.html", {"next": "/lesson_one/colors/page_five",
                                                                 "back": back, "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Colours",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def colors_page_five(request):
    back = "/lesson_one/colors/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/colors/page_five.html", {"next": "/lesson_one/colors/page_six",
                                                                 "back": back, "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Colours",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def colors_page_six(request):
    back = "/lesson_one/colors/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/colors/page_six.html", {"next": "/lesson_one/colors/page_seven",
                                                                "back": back, "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "lesson": "Unit 1: About Me", "title": "Colours",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def colors_page_seven(request):
    back = "/lesson_one/colors/page_six"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/colors/page_seven.html", {"next": "/lesson_one/colors/page_eight",
                                                                  "back": back, "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Colours",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def colors_page_eight(request):
    back = "/lesson_one/colors/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/colors/page_eight.html", {"next": "/lesson_one/colors/page_nine",
                                                                  "back": back, "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Colours",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def colors_page_nine(request):
    back = "/lesson_one/colors/page_eight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/colors/page_nine.html", {"next": "/lesson_one/years/page_one",
                                                                 "back": back, "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Colours",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


# YEARS
def years_page_one(request):
    back = "/lesson_one/colors/page_nine"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        user = User.objects.get(email=request.session['user']['email'])
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter('Years')
        request.session['user'] = UserSerializer(user).data
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_one.html", {"next": "/lesson_one/years/page_two",
                                                               "back": back, "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "lesson": "Unit 1: About Me", "title": "Years",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def years_page_two(request):
    back = "/lesson_one/years/page_one"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/years/page_two.html", {"next": "/lesson_one/years/page_three",
                                                               "back": back, "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "lesson": "Unit 1: About Me", "title": "Years",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def years_page_three(request):
    back = "/lesson_one/years/page_two"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_three.html", {"next": "/lesson_one/years/page_four",
                                                                 "back": back, "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Years",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def years_page_four(request):
    back = "/lesson_one/years/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_four.html", {"next": "/lesson_one/years/page_five",
                                                                "back": back, "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "lesson": "Unit 1: About Me", "title": "Years",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def years_page_five(request):
    back = "/lesson_one/years/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_five.html", {"next": "/lesson_one/years/page_six",
                                                                "back": back, "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "lesson": "Unit 1: About Me", "title": "Years",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def years_page_six(request):
    back = "/lesson_one/years/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/years/page_six.html", {"next": "/lesson_one/years/page_seven",
                                                               "back": back, "lessons": lessons,
                                                               "lesson": "Unit 1: About Me", "title": "Years",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def years_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_seven.html", {"next": "/lesson_one/years/page_eight",
                                                                 "back": "/lesson_one/years/page_six",
                                                                 "solved": solution.solved, "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Years",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def years_page_eight(request):
    back = "/lesson_one/years/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/years/page_eight.html", {"next": "/lesson_one/years/page_nine",
                                                                 "back": back, "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 1: About Me", "title": "Years",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def years_page_nine(request):
    back = "/lesson_one/years/page_eight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/years/page_nine.html", {"next": "/lesson_one/years/page_ten",
                                                                "back": back, "lessons": lessons,
                                                                "lesson": "Unit 1: About Me", "title": "Years",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def years_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_ten.html", {"next": "/lesson_one/years/page_eleven",
                                                               "back": "/lesson_one/years/page_nine",
                                                               "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "lesson": "Unit 1: About Me", "title": "Years",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def years_page_eleven(request):
    back = "/lesson_one/years/page_ten"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_eleven.html", {"next": "/lesson_one/years/page_twelve",
                                                                  "back": back, "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Years",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def years_page_twelve(request):
    back = "/lesson_one/years/page_eleven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/years/page_twelve.html", {"next": "/lesson_one/personal_traits/page_one",
                                                                  "back": back, "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 1: About Me", "title": "Years",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


# PERSONAL TRAITS
def personal_traits_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        user.add_chapter('Personality Traits')
        request.session['user'] = UserSerializer(user).data
        return render(request, "lesson1/personal_traits/page_one.html", {"next": "/lesson_one/personal_traits/page_two",
                                                                         "back": "/lesson_one/years/page_twelve",
                                                                         "solved": solution.solved,
                                                                         "lessons": lessons,
                                                                         "lesson": "Unit 1: About Me",
                                                                         "title": "Personality Traits",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors})


def personal_traits_page_two(request):
    back = "/lesson_one/personal_traits/page_one"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/personal_traits/page_two.html",
                      {"next": "/lesson_one/personal_traits/page_three",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Personality Traits", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def personal_traits_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/personal_traits/page_three.html",
                      {"next": "/lesson_one/personal_traits/page_four",
                       "back": "/lesson_one/personal_traits/page_two",
                       "solved": solution.solved, "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Personality Traits", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def personal_traits_page_four(request):
    back = "/lesson_one/personal_traits/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/personal_traits/page_four.html",
                      {"next": "/lesson_one/personal_traits/page_five",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Personality Traits", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def personal_traits_page_five(request):
    back = "/lesson_one/personal_traits/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/personal_traits/page_five.html",
                      {"next": "/lesson_one/personal_traits/page_six",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Personality Traits", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def personal_traits_page_six(request):
    back = "/lesson_one/personal_traits/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/personal_traits/page_six.html",
                      {"next": "/lesson_one/personal_traits/page_seven",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "Personality Traits", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def personal_traits_page_seven(request):
    back = "/lesson_one/personal_traits/page_six"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/personal_traits/page_seven.html", {"next": "/lesson_one/he_she_it/page_one",
                                                                           "back": back, "solved": solution.solved,
                                                                           "lessons": lessons,
                                                                           "lesson": "Unit 1: About Me",
                                                                           "title": "Personality Traits",
                                                                           "user": request.session['user'],
                                                                           "src": src_ref, "parts": parts,
                                                                           "colors": colors})


def he_she_it_page_one(request):
    back = "/lesson_one/personal_traits/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        user = User.objects.get(email=request.session['user']['email'])
        if not save_solution(user, back) and not user.is_staff:  # marks the previous excersise as solved
            return redirect(back)
        user.add_chapter('He, She, It')  # unlocks the chapter in the menu
        request.session['user'] = UserSerializer(user).data
        return render(request, "lesson1/he_she_it/page_one.html", {"next": "/lesson_one/he_she_it/page_two",
                                                                   "back": back, "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/he_she_it/page_two.html", {"next": "/lesson_one/he_she_it/page_three",
                                                                   "back": "/lesson_one/he_she_it/page_one",
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/he_she_it/page_three.html", {"next": "/lesson_one/he_she_it/page_four",
                                                                     "back": "/lesson_one/he_she_it/page_two",
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "He She It",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/he_she_it/page_four.html", {"next": "/lesson_one/he_she_it/page_five",
                                                                    "back": "/lesson_one/he_she_it/page_three",
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "He She It",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_five.html", {"next": "/lesson_one/he_she_it/page_six",
                                                                    "back": "/lesson_one/he_she_it/page_four",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "He She It",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_six(request):
    back = "/lesson_one/he_she_it/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_six.html", {"next": "/lesson_one/he_she_it/page_seven",
                                                                   "back": back, "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_seven(request):
    back = "/lesson_one/he_she_it/page_six"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_seven.html", {"next": "/lesson_one/he_she_it/page_eight",
                                                                     "back": back, "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "He She It",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_eight.html", {"next": "/lesson_one/he_she_it/page_nine",
                                                                     "back": "/lesson_one/he_she_it/page_seven",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "He She It",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_nine(request):
    back = "/lesson_one/he_she_it/page_eight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_nine.html", {"next": "/lesson_one/he_she_it/page_ten",
                                                                    "back": back, "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 1: About Me", "title": "He She It",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_ten(request):
    back = "/lesson_one/he_she_it/page_nine"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_ten.html", {"next": "/lesson_one/he_she_it/page_eleven",
                                                                   "back": back, "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 1: About Me", "title": "He She It",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_eleven(request):
    back = "/lesson_one/he_she_it/page_ten"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_eleven.html", {"next": "/lesson_one/he_she_it/page_twelve",
                                                                      "back": back, "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me",
                                                                      "title": "He She It",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twelve(request):
    back = "/lesson_one/he_she_it/page_eleven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_twelve.html", {"next": "/lesson_one/he_she_it/page_thirteen",
                                                                      "back": back, "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me",
                                                                      "title": "He She It",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirteen(request):
    back = "/lesson_one/he_she_it/page_twelve"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_thirteen.html", {"next": "/lesson_one/he_she_it/page_fourteen",
                                                                        "back": back, "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "He She It",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


def he_she_it_page_fourteen(request):
    back = "/lesson_one/he_she_it/page_thirteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_fourteen.html", {"next": "/lesson_one/he_she_it/page_fifteen",
                                                                        "back": back, "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "He She It",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


def he_she_it_page_fifteen(request):
    back = "/lesson_one/he_she_it/page_fourteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_fifteen.html", {"next": "/lesson_one/he_she_it/page_sixteen",
                                                                       "back": back, "lessons": lessons,
                                                                       "lesson": "Unit 1: About Me",
                                                                       "title": "He She It",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts,
                                                                       "colors": colors})


def he_she_it_page_sixteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_sixteen.html", {"next": "/lesson_one/he_she_it/page_seventeen",
                                                                       "back": "/lesson_one/he_she_it/page_fifteen",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 1: About Me",
                                                                       "title": "He She It",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts,
                                                                       "colors": colors})


def he_she_it_page_seventeen(request):
    back = "/lesson_one/he_she_it/page_sixteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_seventeen.html", {"next": "/lesson_one/he_she_it/page_eighteen",
                                                                         "back": back, "solved": solution.solved,
                                                                         "lessons": lessons,
                                                                         "lesson": "Unit 1: About Me",
                                                                         "title": "He She It",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors})


def he_she_it_page_eighteen(request):
    back = "/lesson_one/he_she_it/page_seventeen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_eighteen.html", {"next": "/lesson_one/he_she_it/page_nineteen",
                                                                        "back": back, "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "He She It",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


def he_she_it_page_nineteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/he_she_it/page_nineteen.html", {"next": "/lesson_one/he_she_it/page_twenty",
                                                                        "back": "/lesson_one/he_she_it/page_eighteen",
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "He She It",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


def he_she_it_page_twenty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_twenty.html", {"next": "/lesson_one/he_she_it/page_twentyone",
                                                                      "back": "/lesson_one/he_she_it/page_nineteen",
                                                                      "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me",
                                                                      "title": "He She It",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentyone(request):
    back = "/lesson_one/he_she_it/page_twenty"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_twentyone.html", {"next": "/lesson_one/he_she_it/page_twentytwo",
                                                                         "back": back, "lessons": lessons,
                                                                         "lesson": "Unit 1: About Me",
                                                                         "title": "He She It",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors})


def he_she_it_page_twentytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_twentytwo.html",
                      {"next": "/lesson_one/he_she_it/page_twentythree",
                       "back": "/lesson_one/he_she_it/page_twentyone",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentythree(request):
    back = "/lesson_one/he_she_it/page_twentytwo"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_twentythree.html",
                      {"next": "/lesson_one/he_she_it/page_twentyfour",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentyfour(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_twentyfour.html",
                      {"next": "/lesson_one/he_she_it/page_twentyfive",
                       "back": "/lesson_one/he_she_it/page_twentythree",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentyfive(request):
    back = "/lesson_one/he_she_it/page_twentyfour"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_twentyfive.html",
                      {"next": "/lesson_one/he_she_it/page_twentysix",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentysix(request):
    back = "/lesson_one/he_she_it/page_twentyfive"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(User.objects.get(email=request.session['user']['email']), back):
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_twentysix.html",
                      {"next": "/lesson_one/he_she_it/page_twentyseven",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentyseven(request):
    back = "/lesson_one/he_she_it/page_twentysix"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_twentyseven.html",
                      {"next": "/lesson_one/he_she_it/page_twentyeight",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentyeight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_twentyeight.html",
                      {"next": "/lesson_one/he_she_it/page_twentynine",
                       "back": "/lesson_one/he_she_it/page_twentyseven",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_twentynine(request):
    back = "/lesson_one/he_she_it/page_twentyeight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_twentynine.html", {"next": "/lesson_one/he_she_it/page_thirty",
                                                                          "back": back, "lessons": lessons,
                                                                          "lesson": "Unit 1: About Me",
                                                                          "title": "He She It",
                                                                          "user": request.session['user'],
                                                                          "src": src_ref, "parts": parts,
                                                                          "colors": colors})


def he_she_it_page_thirty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/he_she_it/page_thirty.html", {"next": "/lesson_one/he_she_it/page_thirtyone",
                                                                      "back": "/lesson_one/he_she_it/page_twentynine",
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 1: About Me",
                                                                      "title": "He She It",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_thirtyone.html", {"next": "/lesson_one/he_she_it/page_thirtytwo",
                                                                         "back": "/lesson_one/he_she_it/page_thirty",
                                                                         "solved": solution.solved, "lessons": lessons,
                                                                         "lesson": "Unit 1: About Me",
                                                                         "title": "He She It",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors})


def he_she_it_page_thirtytwo(request):
    back = "/lesson_one/he_she_it/page_thirtyone"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_thirtytwo.html",
                      {"next": "/lesson_one/he_she_it/page_thirtythree",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtythree(request):
    back = "/lesson_one/he_she_it/page_thirtytwo"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_thirtythree.html",
                      {"next": "/lesson_one/he_she_it/page_thirtyfour",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtyfour(request):
    back = "/lesson_one/he_she_it/page_thirtythree"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_thirtyfour.html",
                      {"next": "/lesson_one/he_she_it/page_thirtyfive",
                       "back": back, "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtyfive(request):
    back = "/lesson_one/he_she_it/page_thirtyfour"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson1/he_she_it/page_thirtyfive.html",
                      {"next": "/lesson_one/he_she_it/page_thirtysix",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtysix(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/he_she_it/page_thirtysix.html",
                      {"next": "/lesson_one/he_she_it/page_thirtyseven",
                       "back": "/lesson_one/he_she_it/page_thirtyfive",
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtyseven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson1/he_she_it/page_thirtyseven.html",
                      {"next": "/lesson_one/he_she_it/page_thirtyeight",
                       "back": "/lesson_one/he_she_it/page_thirtysix",
                       "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtyeight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_thirtyeight.html",
                      {"next": "/lesson_one/he_she_it/page_thirtynine",
                       "back": "/lesson_one/he_she_it/page_thirtyseven",
                       "solved": solution.solved, "lessons": lessons,
                       "lesson": "Unit 1: About Me", "title": "He She It", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_thirtynine(request):
    back = "/lesson_one/he_she_it/page_thirtyeight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_thirtynine.html", {"next": "/lesson_one/he_she_it/page_forty",
                                                                          "back": back, "solved": solution.solved,
                                                                          "lessons": lessons,
                                                                          "lesson": "Unit 1: About Me",
                                                                          "title": "He She It",
                                                                          "user": request.session['user'],
                                                                          "src": src_ref, "parts": parts,
                                                                          "colors": colors})


def he_she_it_page_forty(request):
    back = "/lesson_one/he_she_it/page_thirtynine"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_forty.html", {"next": "/lesson_one/he_she_it/page_fortyone",
                                                                     "back": back, "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 1: About Me", "title": "He She It",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors})


def he_she_it_page_fortyone(request):
    back = "/lesson_one/he_she_it/page_forty"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_fortyone.html", {"next": "/lesson_one/he_she_it/page_fortytwo",
                                                                        "back": back, "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "He She It",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


def he_she_it_page_fortytwo(request):
    back = "/lesson_one/he_she_it/page_fortyone"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson1/he_she_it/page_fortytwo.html", {"next": "/lesson_two/title",
                                                                        "back": back, "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 1: About Me",
                                                                        "title": "He She It",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts,
                                                                        "colors": colors})


# UNIT 2

def lesson_two_title(request):
    back = "/lesson_one/he_she_it/page_fortytwo"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        if request.method == "GET":
            return render(request, "lesson2/title_page.html",
                          {"next": "/lesson_two/day_week_month/page_one", "back": back,
                           "lessons": lessons,
                           "lesson": "Unit 2", "title": "", "user": request.session['user']})


def day_week_month_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        user.add_chapter('Day Week Month')
        return render(request, "lesson2/day_week_month/page_one.html", {"next": "/lesson_two/day_week_month/page_two",
                                                                        "back": "/lesson_two/title",
                                                                        "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Day Week Month",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def day_week_month_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/day_week_month/page_two.html", {"next": "/lesson_two/day_week_month/page_three",
                                                                        "back": "/lesson_two/day_week_month/page_one",
                                                                        "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Day Week Month",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def day_week_month_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/day_week_month/page_three.html",
                      {"next": "/lesson_two/day_week_month/page_four",
                       "back": "/lesson_two/day_week_month/page_two",
                       "lessons": lessons,
                       "lesson": "Unit 2", "title": "Day Week Month", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def day_week_month_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/day_week_month/page_four.html", {"next": "/lesson_two/day_week_month/page_five",
                                                                         "back": "/lesson_two/day_week_month/page_three",
                                                                         "lessons": lessons, "solved": solution.solved,
                                                                         "lesson": "Unit 2", "title": "Day Week Month",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def day_week_month_page_five(request):
    back = "/lesson_two/day_week_month/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/day_week_month/page_five.html", {"next": "/lesson_two/day_week_month/page_six",
                                                                         "back": back,
                                                                         "lessons": lessons, "solved": solution.solved,
                                                                         "lesson": "Unit 2", "title": "Day Week Month",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def day_week_month_page_six(request):
    back = "/lesson_two/day_week_month/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/day_week_month/page_six.html", {"next": "/lesson_two/day_week_month/page_seven",
                                                                        "back": back,
                                                                        "lessons": lessons, "solved": solution.solved,
                                                                        "lesson": "Unit 2", "title": "Day Week Month",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def day_week_month_page_seven(request):
    back = "/lesson_two/day_week_month/page_six"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/day_week_month/page_seven.html",
                      {"next": "/lesson_two/day_week_month/page_eight",
                       "back": back,
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Day Week Month", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def day_week_month_page_eight(request):
    back = "/lesson_two/day_week_month/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/day_week_month/page_eight.html",
                      {"next": "/lesson_two/day_week_month/page_nine",
                       "back": back,
                       "lessons": lessons,
                       "lesson": "Unit 2", "title": "Day Week Month", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def day_week_month_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/day_week_month/page_nine.html", {"next": "/lesson_two/day_week_month/page_ten",
                                                                         "back": "/lesson_two/day_week_month/page_eight",
                                                                         "lessons": lessons, "solved": solution.solved,
                                                                         "lesson": "Unit 2", "title": "Day Week Month",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def day_week_month_page_ten(request):
    back = "/lesson_two/day_week_month/page_nine"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        user.add_chapter('Day Week Month')
        return render(request, "lesson2/day_week_month/page_ten.html",
                      {"next": "/lesson_two/day_week_month/page_eleven",
                       "back": back, "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Day Week Month", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def day_week_month_page_eleven(request):
    back = "/lesson_two/day_week_month/page_ten"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        user.add_chapter('Day Week Month')
        return render(request, "lesson2/day_week_month/page_eleven.html",
                      {"next": "/lesson_two/day_week_month/page_twelve",
                       "back": back, "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Day Week Month", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def day_week_month_page_twelve(request):
    back = "/lesson_two/day_week_month/page_eleven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        user.add_chapter('Day Week Month')
        return render(request, "lesson2/day_week_month/page_twelve.html", {"next": "/lesson_two/articles/page_one",
                                                                           "back": back, "lessons": lessons,
                                                                           "solved": solution.solved,
                                                                           "lesson": "Unit 2",
                                                                           "title": "Day Week Month",
                                                                           "user": request.session['user'],
                                                                           "src": src_ref, "parts": parts,
                                                                           "colors": colors
                                                                           })


def articles_page_one(request):
    back = "/lesson_two/day_week_month/page_twelve"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter('Articles')
        return render(request, "lesson2/articles/page_one.html", {"next": "/lesson_two/articles/page_two",
                                                                  "back": back, "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Articles",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def articles_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_two.html", {"next": "/lesson_two/articles/page_three",
                                                                  "back": "/lesson_two/articles/page_one",
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Articles",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def articles_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_three.html", {"next": "/lesson_two/articles/page_four",
                                                                    "back": "/lesson_two/articles/page_two",
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 2", "title": "Articles",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def articles_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_four.html", {"next": "/lesson_two/articles/page_five",
                                                                   "back": "/lesson_two/articles/page_three",
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 2", "title": "Articles",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def articles_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_five.html", {"next": "/lesson_two/articles/page_six",
                                                                   "back": "/lesson_two/articles/page_four",
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 2", "title": "Articles",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def articles_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_six.html", {"next": "/lesson_two/articles/page_seven",
                                                                  "back": "/lesson_two/articles/page_five",
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Articles",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def articles_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_seven.html", {"next": "/lesson_two/articles/page_eight",
                                                                    "back": "/lesson_two/articles/page_six",
                                                                    "lessons": lessons,
                                                                    "solved": solution.solved,
                                                                    "lesson": "Unit 2", "title": "Articles",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def articles_page_eight(request):
    back = "/lesson_two/articles/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_eight.html", {"next": "/lesson_two/articles/page_nine",
                                                                    "back": back, "lessons": lessons,
                                                                    "solved": solution.solved,
                                                                    "lesson": "Unit 2", "title": "Articles",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def articles_page_nine(request):
    back = "/lesson_two/articles/page_eight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/articles/page_nine.html", {"next": "/lesson_two/articles/page_ten",
                                                                   "back": back, "lessons": lessons,
                                                                   "lesson": "Unit 2", "title": "Articles",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def articles_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_ten.html", {"next": "/lesson_two/articles/page_eleven",
                                                                  "back": "/lesson_two/articles/page_nine",
                                                                  "solved": solution.solved, "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Articles",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def articles_page_eleven(request):
    back = "/lesson_two/articles/page_ten"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/articles/page_eleven.html", {"next": "/lesson_two/articles/page_twelve",
                                                                     "back": back, "lessons": lessons,
                                                                     "lesson": "Unit 2", "title": "Articles",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def articles_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_twelve.html", {"next": "/lesson_two/articles/page_thirteen",
                                                                     "back": "/lesson_two/articles/page_eleven",
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 2", "title": "Articles * Extra",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def articles_page_thirteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_thirteen.html", {"next": "/lesson_two/articles/page_fourteen",
                                                                       "back": "/lesson_two/articles/page_twelve",
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 2", "title": "Articles * Extra",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def articles_page_fourteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_fourteen.html", {"next": "/lesson_two/articles/page_fifteen",
                                                                       "back": "/lesson_two/articles/page_thirteen",
                                                                       "lessons": lessons, "solved": solution.solved,
                                                                       "lesson": "Unit 2", "title": "Articles * Extra",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def articles_page_fifteen(request):
    back = "/lesson_two/articles/page_fourteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_fifteen.html", {"next": "/lesson_two/articles/page_sixteen",
                                                                      "back": back, "lessons": lessons,
                                                                      "solved": solution.solved,
                                                                      "lesson": "Unit 2", "title": "Articles * Extra",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors
                                                                      })


def articles_page_sixteen(request):
    back = "/lesson_two/articles/page_fifteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/articles/page_sixteen.html", {"next": "/lesson_two/articles/page_seventeen",
                                                                      "back": back, "lessons": lessons,
                                                                      "lesson": "Unit 2", "title": "Articles * Extra",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors
                                                                      })


def articles_page_seventeen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_seventeen.html", {"next": "/lesson_two/articles/page_eighteen",
                                                                        "back": "/lesson_two/articles/page_sixteen",
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Articles * Extra",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def articles_page_eighteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_eighteen.html", {"next": "/lesson_two/articles/page_nineteen",
                                                                       "back": "/lesson_two/articles/page_seventeen",
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 2", "title": "Articles * Extra",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def articles_page_nineteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_nineteen.html", {"next": "/lesson_two/articles/page_twenty",
                                                                       "back": "/lesson_two/articles/page_eighteen",
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 2", "title": "Articles * Extra",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def articles_page_twenty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/articles/page_twenty.html", {"next": "/lesson_two/articles/page_twentyone",
                                                                     "back": "/lesson_two/articles/page_nineteen",
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 2", "title": "Articles * Extra",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def articles_page_twentyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_twentyone.html", {"next": "/lesson_two/articles/page_twentytwo",
                                                                        "back": "/lesson_two/articles/page_twenty",
                                                                        "solved": solution.solved, "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Articles * Extra",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def articles_page_twentytwo(request):
    back = "/lesson_two/articles/page_twentyone"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_twentytwo.html", {"next": "/lesson_two/articles/page_twentythree",
                                                                        "back": back,
                                                                        "solved": solution.solved, "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Articles * Extra",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def articles_page_twentythree(request):
    back = "/lesson_two/articles/page_twentytwo"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/articles/page_twentythree.html", {"next": "/lesson_two/family/page_one",
                                                                          "back": back,
                                                                          "solved": solution.solved, "lessons": lessons,
                                                                          "lesson": "Unit 2",
                                                                          "title": "Articles * Extra",
                                                                          "user": request.session['user'],
                                                                          "src": src_ref, "parts": parts,
                                                                          "colors": colors
                                                                          })


def family_page_one(request):
    back = "/lesson_two/articles/page_twentythree"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter('Family Members')
        return render(request, "lesson2/family/page_one.html", {"next": "/lesson_two/family/page_two",
                                                                "back": back, "lessons": lessons,
                                                                "lesson": "Unit 2", "title": "Family Members",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def family_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_two.html", {"next": "/lesson_two/family/page_three",
                                                                "back": "/lesson_two/family/page_one",
                                                                "lessons": lessons,
                                                                "lesson": "Unit 2", "title": "Family Members",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def family_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_three.html", {"next": "/lesson_two/family/page_four",
                                                                  "back": "/lesson_two/family/page_two",
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Family Members",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def family_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_four.html", {"next": "/lesson_two/family/page_five",
                                                                 "back": "/lesson_two/family/page_three",
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 2", "title": "Family Members",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def family_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_five.html", {"next": "/lesson_two/family/page_six",
                                                                 "back": "/lesson_two/family/page_four",
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 2", "title": "Family Members",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def family_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_six.html", {"next": "/lesson_two/family/page_seven",
                                                                "back": "/lesson_two/family/page_five",
                                                                "lessons": lessons,
                                                                "lesson": "Unit 2", "title": "Family Members",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def family_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_seven.html", {"next": "/lesson_two/family/page_eight",
                                                                  "back": "/lesson_two/family/page_six",
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Family Members",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def family_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_eight.html", {"next": "/lesson_two/family/page_nine",
                                                                  "back": "/lesson_two/family/page_seven",
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Family Members",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def family_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_nine.html", {"next": "/lesson_two/family/page_ten",
                                                                 "back": "/lesson_two/family/page_eight",
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 2", "title": "Family Members",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def family_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/family/page_ten.html", {"next": "/lesson_two/family/page_eleven",
                                                                "back": "/lesson_two/family/page_nine",
                                                                "lessons": lessons,
                                                                "lesson": "Unit 2", "title": "Family Members",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def family_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/family/page_eleven.html", {"next": "/lesson_two/family/page_twelve",
                                                                   "back": "/lesson_two/family/page_ten",
                                                                   "lessons": lessons, "solved": solution.solved,
                                                                   "lesson": "Unit 2", "title": "Family Members",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def family_page_twelve(request):
    back = "/lesson_two/family/page_eleven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/family/page_twelve.html", {"next": "/lesson_two/family/page_thirteen",
                                                                   "back": back, "lessons": lessons,
                                                                   "solved": solution.solved,
                                                                   "lesson": "Unit 2", "title": "Family Members",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def family_page_thirteen(request):
    back = "/lesson_two/family/page_twelve"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/family/page_thirteen.html", {"next": "/lesson_two/family/page_fourteen",
                                                                     "back": back, "lessons": lessons,
                                                                     "solved": solution.solved,
                                                                     "lesson": "Unit 2", "title": "Family Members",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def family_page_fourteen(request):
    back = "/lesson_two/family/page_thirteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/family/page_fourteen.html", {"next": "/lesson_two/family/page_fifteen",
                                                                     "back": back, "lessons": lessons,
                                                                     "solved": solution.solved,
                                                                     "lesson": "Unit 2", "title": "Family Members",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def family_page_fifteen(request):
    back = "/lesson_two/family/page_fourteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/family/page_fifteen.html", {"next": "/lesson_two/family/page_sixteen",
                                                                    "back": back, "lessons": lessons,
                                                                    "solved": solution.solved,
                                                                    "lesson": "Unit 2", "title": "Family Members",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def family_page_sixteen(request):
    back = "/lesson_two/family/page_fifteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/family/page_sixteen.html", {"next": "/lesson_two/clothes/page_one",
                                                                    "back": back, "lessons": lessons,
                                                                    "solved": solution.solved,
                                                                    "lesson": "Unit 2", "title": "Family Members",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def clothes_page_one(request):
    back = "/lesson_two/family/page_sixteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter('Clothes')
        return render(request, "lesson2/clothes/page_one.html", {"next": "/lesson_two/clothes/page_two",
                                                                 "back": back, "lessons": lessons,
                                                                 "lesson": "Unit 2", "title": "Clothes",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def clothes_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/clothes/page_two.html", {"next": "/lesson_two/clothes/page_three",
                                                                 "back": "/lesson_two/clothes/page_one",
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 2", "title": "Clothes",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def clothes_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_three.html", {"next": "/lesson_two/clothes/page_four",
                                                                   "back": "/lesson_two/clothes/page_two",
                                                                   "lessons": lessons, "solved": solution.solved,
                                                                   "lesson": "Unit 2", "title": "Clothes",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def clothes_page_four(request):
    back = "/lesson_two/clothes/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/clothes/page_four.html", {"next": "/lesson_two/clothes/page_five",
                                                                  "back": back,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 2", "title": "Clothes",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def clothes_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_five.html", {"next": "/lesson_two/clothes/page_six",
                                                                  "back": "/lesson_two/clothes/page_four",
                                                                  "lessons": lessons, "solved": solution.solved,
                                                                  "lesson": "Unit 2", "title": "Clothes",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def clothes_page_six(request):
    back = "/lesson_two/clothes/page_five"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/clothes/page_six.html", {"next": "/lesson_two/clothes/page_seven",
                                                                 "back": back,
                                                                 "lessons": lessons,
                                                                 "lesson": "Unit 2", "title": "Clothes",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def clothes_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_seven.html", {"next": "/lesson_two/clothes/page_eight",
                                                                   "back": "/lesson_two/clothes/page_six",
                                                                   "lessons": lessons, "solved": solution.solved,
                                                                   "lesson": "Unit 2", "title": "Clothes",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def clothes_page_eight(request):
    back = "/lesson_two/clothes/page_seven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/clothes/page_eight.html", {"next": "/lesson_two/clothes/page_nine",
                                                                   "back": back,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 2", "title": "Clothes",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def clothes_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_nine.html", {"next": "/lesson_two/clothes/page_ten",
                                                                  "back": "/lesson_two/clothes/page_eight",
                                                                  "lessons": lessons, "solved": solution.solved,
                                                                  "lesson": "Unit 2", "title": "Clothes",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def clothes_page_ten(request):
    back = "/lesson_two/clothes/page_nine"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_ten.html", {"next": "/lesson_two/clothes/page_eleven",
                                                                 "back": back,
                                                                 "lessons": lessons, "solved": solution.solved,
                                                                 "lesson": "Unit 2", "title": "Clothes",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def clothes_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_eleven.html", {"next": "/lesson_two/clothes/page_twelve",
                                                                    "back": "/lesson_two/clothes/page_ten",
                                                                    "lessons": lessons, "solved": solution.solved,
                                                                    "lesson": "Unit 2", "title": "Clothes",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def clothes_page_twelve(request):
    back = "/lesson_two/clothes/page_eleven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_twelve.html", {"next": "/lesson_two/clothes/page_thirteen",
                                                                    "back": back,
                                                                    "lessons": lessons, "solved": solution.solved,
                                                                    "lesson": "Unit 2", "title": "Clothes",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def clothes_page_thirteen(request):
    back = "/lesson_two/clothes/page_twelve"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_thirteen.html", {"next": "/lesson_two/clothes/page_fourteen",
                                                                      "back": back,
                                                                      "lessons": lessons, "solved": solution.solved,
                                                                      "lesson": "Unit 2", "title": "Clothes",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors
                                                                      })


def clothes_page_fourteen(request):
    back = "/lesson_two/clothes/page_thirteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_fourteen.html", {"next": "/lesson_two/clothes/page_fifteen",
                                                                      "back": back,
                                                                      "lessons": lessons, "solved": solution.solved,
                                                                      "lesson": "Unit 2", "title": "Clothes",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors
                                                                      })


def clothes_page_fifteen(request):
    back = "/lesson_two/clothes/page_fourteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/clothes/page_fifteen.html", {"next": "/lesson_two/time/page_one",
                                                                     "back": back,
                                                                     "lessons": lessons, "solved": solution.solved,
                                                                     "lesson": "Unit 2", "title": "Clothes",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def time_page_one(request):
    back = "/lesson_two/clothes/page_fifteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter("Time")
        return render(request, "lesson2/time/page_one.html", {"next": "/lesson_two/time/page_two",
                                                              "back": back, "lessons": lessons,
                                                              "lesson": "Unit 2", "title": "Time",
                                                              "user": request.session['user'],
                                                              "src": src_ref, "parts": parts, "colors": colors
                                                              })


def time_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/time/page_two.html", {"next": "/lesson_two/time/page_three",
                                                              "back": "/lesson_two/time/page_one", "lessons": lessons,
                                                              "lesson": "Unit 2", "title": "Time",
                                                              "user": request.session['user'],
                                                              "src": src_ref, "parts": parts, "colors": colors
                                                              })


def time_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/time/page_three.html", {"next": "/lesson_two/time/page_four",
                                                                "back": "/lesson_two/time/page_two", "lessons": lessons,
                                                                "lesson": "Unit 2", "title": "Time",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def time_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/time/page_four.html", {"next": "/lesson_two/time/page_five",
                                                               "back": "/lesson_two/time/page_three",
                                                               "lessons": lessons,
                                                               "lesson": "Unit 2", "title": "Time",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def time_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/time/page_five.html", {"next": "/lesson_two/time/page_six",
                                                               "back": "/lesson_two/time/page_four", "lessons": lessons,
                                                               "lesson": "Unit 2", "title": "Time",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def time_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/time/page_six.html", {"next": "/lesson_two/time/page_seven",
                                                              "back": "/lesson_two/time/page_five", "lessons": lessons,
                                                              "lesson": "Unit 2", "title": "Time",
                                                              "user": request.session['user'],
                                                              "src": src_ref, "parts": parts, "colors": colors
                                                              })


def time_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/time/page_seven.html", {"next": "/lesson_two/time/page_eight",
                                                                "back": "/lesson_two/time/page_six", "lessons": lessons,
                                                                "lesson": "Unit 2", "title": "Time",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def time_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/time/page_eight.html", {"next": "/lesson_two/time/page_nine",
                                                                "back": "/lesson_two/time/page_seven",
                                                                "lessons": lessons,
                                                                "lesson": "Unit 2", "title": "Time",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def time_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/time/page_nine.html", {"next": "/lesson_two/time/page_ten",
                                                               "back": "/lesson_two/time/page_eight",
                                                               "solved": solution.solved, "lessons": lessons,
                                                               "lesson": "Unit 2", "title": "Time",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def time_page_ten(request):
    back = "/lesson_two/time/page_nine"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/time/page_ten.html", {"next": "/lesson_two/present_simple/page_one",
                                                              "back": back, "solved": solution.solved,
                                                              "lessons": lessons,
                                                              "lesson": "Unit 2", "title": "Time",
                                                              "user": request.session['user'],
                                                              "src": src_ref, "parts": parts, "colors": colors
                                                              })


def present_simple_page_one(request):
    back = "/lesson_two/time/page_ten"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        user.add_chapter("Present Simple")
        return render(request, "lesson2/present_simple/page_one.html", {"next": "/lesson_two/present_simple/page_two",
                                                                        "back": back, "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Present Simple",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def present_simple_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/present_simple/page_two.html", {"next": "/lesson_two/present_simple/page_three",
                                                                        "back": "/lesson_two/present_simple/page_one",
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Present Simple",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def present_simple_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/present_simple/page_three.html",
                      {"next": "/lesson_two/present_simple/page_four",
                       "back": "/lesson_two/present_simple/page_two", "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/present_simple/page_four.html", {"next": "/lesson_two/present_simple/page_five",
                                                                         "back": "/lesson_two/present_simple/page_three",
                                                                         "lessons": lessons, "solved": solution.solved,
                                                                         "lesson": "Unit 2", "title": "Present Simple",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def present_simple_page_five(request):
    back = "/lesson_two/present_simple/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/present_simple/page_five.html", {"next": "/lesson_two/present_simple/page_six",
                                                                         "back": back, "lessons": lessons,
                                                                         "lesson": "Unit 2", "title": "Present Simple",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def present_simple_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/present_simple/page_six.html", {"next": "/lesson_two/present_simple/page_seven",
                                                                        "back": "/lesson_two/present_simple/page_five",
                                                                        "lessons": lessons, "solved": solution.solved,
                                                                        "lesson": "Unit 2", "title": "Present Simple",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def present_simple_page_seven(request):
    back = "/lesson_two/present_simple/page_six"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/present_simple/page_seven.html",
                      {"next": "/lesson_two/present_simple/page_eight",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/present_simple/page_eight.html",
                      {"next": "/lesson_two/present_simple/page_nine",
                       "back": "/lesson_two/present_simple/page_seven",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_nine(request):
    back = "/lesson_two/present_simple/page_eight"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/present_simple/page_nine.html", {"next": "/lesson_two/present_simple/page_ten",
                                                                         "back": back, "lessons": lessons,
                                                                         "lesson": "Unit 2", "title": "Present Simple",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def present_simple_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/present_simple/page_ten.html",
                      {"next": "/lesson_two/present_simple/page_eleven",
                       "back": "/lesson_two/present_simple/page_nine", "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/present_simple/page_eleven.html",
                      {"next": "/lesson_two/present_simple/page_twelve",
                       "back": "/lesson_two/present_simple/page_ten",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_twelve(request):
    back = "/lesson_two/present_simple/page_eleven"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/present_simple/page_twelve.html",
                      {"next": "/lesson_two/present_simple/page_thirteen",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_thirteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/present_simple/page_thirteen.html",
                      {"next": "/lesson_two/present_simple/page_fourteen",
                       "back": "/lesson_two/present_simple/page_twelve", "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_fourteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/present_simple/page_fourteen.html",
                      {"next": "/lesson_two/present_simple/page_fifteen",
                       "back": "/lesson_two/present_simple/page_thirteen", "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_fifteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/present_simple/page_fifteen.html",
                      {"next": "/lesson_two/present_simple/page_sixteen",
                       "back": "/lesson_two/present_simple/page_fourteen", "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_sixteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/present_simple/page_sixteen.html",
                      {"next": "/lesson_two/present_simple/page_seventeen",
                       "back": "/lesson_two/present_simple/page_fifteen",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def present_simple_page_seventeen(request):
    back = "/lesson_two/present_simple/page_sixteen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        if not save_solution(user, back) and not user.is_staff:
            return redirect(back)
        return render(request, "lesson2/present_simple/page_seventeen.html",
                      {"next": "/lesson_two/daily_routines/page_one",
                       "back": back, "lessons": lessons,
                       "lesson": "Unit 2", "title": "Present Simple", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def daily_routines_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/daily_routines/page_one.html", {"next": "/lesson_two/daily_routines/page_two",
                                                                        "back": "/lesson_two/present_simple/page_seventeen",
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Daily Routines",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def daily_routines_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/daily_routines/page_two.html", {"next": "/lesson_two/daily_routines/page_three",
                                                                        "back": "/lesson_two/daily_routines/page_one",
                                                                        "lessons": lessons, "solved": solution.solved,
                                                                        "lesson": "Unit 2", "title": "Daily Routines",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def daily_routines_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/daily_routines/page_three.html",
                      {"next": "/lesson_two/daily_routines/page_four",
                       "back": "/lesson_two/daily_routines/page_two",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def daily_routines_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/daily_routines/page_four.html", {"next": "/lesson_two/daily_routines/page_five",
                                                                         "back": "/lesson_two/daily_routines/page_three",
                                                                         "lessons": lessons, "solved": solution.solved,
                                                                         "lesson": "Unit 2", "title": "Daily Routines",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def daily_routines_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/daily_routines/page_five.html", {"next": "/lesson_two/daily_routines/page_six",
                                                                         "back": "/lesson_two/daily_routines/page_four",
                                                                         "lessons": lessons,
                                                                         "lesson": "Unit 2", "title": "Daily Routines",
                                                                         "user": request.session['user'],
                                                                         "src": src_ref, "parts": parts,
                                                                         "colors": colors
                                                                         })


def daily_routines_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/daily_routines/page_six.html",
                      {"next": "/lesson_two/daily_routines/page_seven",
                       "back": "/lesson_two/daily_routines/page_five",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def daily_routines_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/daily_routines/page_seven.html",
                      {"next": "/lesson_two/daily_routines/page_eight",
                       "back": "/lesson_two/daily_routines/page_six",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def daily_routines_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/daily_routines/page_eight.html",
                      {"next": "/lesson_two/occupations/page_one",
                       "back": "/lesson_two/daily_routines/page_seven",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def occupations_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/occupations/page_one.html",
                      {"next": "/lesson_two/occupations/page_two",
                       "back": "/lesson_two/daily_routines/page_eight",
                       "lessons": lessons,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def occupations_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/occupations/page_two.html",
                      {"next": "/lesson_two/occupations/page_three",
                       "back": "/lesson_two/occupations/page_one",
                       "lessons": lessons,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def occupations_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/occupations/page_three.html",
                      {"next": "/lesson_two/occupations/page_four",
                       "back": "/lesson_two/occupations/page_two",
                       "lessons": lessons,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def occupations_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/occupations/page_four.html",
                      {"next": "/lesson_two/occupations/page_five",
                       "back": "/lesson_two/occupations/page_three",
                       "lessons": lessons,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def occupations_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/occupations/page_six.html",
                      {"next": "/lesson_two/occupations/page_six",
                       "back": "/lesson_two/occupations/page_four",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def occupations_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/occupations/page_seven.html",
                      {"next": "/lesson_two/occupations/page_seven",
                       "back": "/lesson_two/occupations/page_five",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


def occupations_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson2/occupations/page_eight.html",
                      {"next": "/coming_soon",
                       "back": "/lesson_two/occupations/page_six",
                       "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts,
                       "colors": colors
                       })


# UNIT 3
def lesson_three_title(request):
    if request.method == "GET":
        return render(request, "lesson3/title_page.html", {"next": "/lesson_three/pronouns/page_one",
                                                           "back": "/lesson_two/present_simple/page_seventeen",
                                                           "lessons": lessons,
                                                           "lesson": "Unit 3: Let's Eat", "title": "",
                                                           "user": request.session['user']
                                                           })


def pronouns_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        user.add_chapter("Pronouns")
        return render(request, "lesson3/pronouns/page_one.html", {"next": "/lesson_three/pronouns/page_two",
                                                                  "back": "/lesson_three/title",
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def pronouns_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson3/pronouns/page_two.html", {"next": "/lesson_three/pronouns/page_three",
                                                                  "back": "/lesson_three/pronouns/page_one",
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def pronouns_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson3/pronouns/page_three.html", {"next": "/lesson_three/pronouns/page_four",
                                                                    "back": "/lesson_three/pronouns/page_two",
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def pronouns_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user,
                                          request.path)  # @SpeedaRJ če je contextu (ta dict spodej) solution dodaj ta stavek
        return render(request, "lesson3/pronouns/page_four.html", {"next": "/lesson_three/pronouns/page_five",
                                                                   "back": "/lesson_three/pronouns/page_three",
                                                                   "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def pronouns_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_five.html", {"next": "/lesson_three/pronouns/page_six",
                                                                   "back": "/lesson_three/pronouns/page_four",
                                                                   "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def pronouns_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_six.html", {"next": "/lesson_three/pronouns/page_seven",
                                                                  "back": "/lesson_three/pronouns/page_five",
                                                                  "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def pronouns_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_seven.html", {"next": "/lesson_three/pronouns/page_eight",
                                                                    "back": "/lesson_three/pronouns/page_six",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def pronouns_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_eight.html", {"next": "/lesson_three/pronouns/page_nine",
                                                                    "back": "/lesson_three/pronouns/page_seven",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def pronouns_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_nine.html", {"next": "/lesson_three/pronouns/page_ten",
                                                                   "back": "/lesson_three/pronouns/page_eight",
                                                                   "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def pronouns_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_ten.html", {"next": "/lesson_three/pronouns/page_eleven",
                                                                  "back": "/lesson_three/pronouns/page_nine",
                                                                  "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def pronouns_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_eleven.html", {"next": "/lesson_three/pronouns/page_twelve",
                                                                     "back": "/lesson_three/pronouns/page_ten",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def pronouns_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twelve.html", {"next": "/lesson_three/pronouns/page_thirteen",
                                                                     "back": "/lesson_three/pronouns/page_eleven",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def pronouns_page_thirteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_thirteen.html", {"next": "/lesson_three/pronouns/page_fourteen",
                                                                       "back": "/lesson_three/pronouns/page_twelve",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat",
                                                                       "title": "Pronouns",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def pronouns_page_fourteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_fourteen.html", {"next": "/lesson_three/pronouns/page_sixteen",
                                                                       "back": "/lesson_three/pronouns/page_thirteen",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat",
                                                                       "title": "Pronouns",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def pronouns_page_sixteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_sixteen.html", {"next": "/lesson_three/pronouns/page_seventeen",
                                                                      "back": "/lesson_three/pronouns/page_fourteen",
                                                                      "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 3: Let's Eat",
                                                                      "title": "Pronouns",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors
                                                                      })


def pronouns_page_seventeen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_seventeen.html", {"next": "/lesson_three/pronouns/page_eighteen",
                                                                        "back": "/lesson_three/pronouns/page_sixteen",
                                                                        "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 3: Let's Eat",
                                                                        "title": "Pronouns",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def pronouns_page_eighteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_eighteen.html", {"next": "/lesson_three/pronouns/page_nineteen",
                                                                       "back": "/lesson_three/pronouns/page_seventeen",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat",
                                                                       "title": "Pronouns",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def pronouns_page_nineteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_nineteen.html", {"next": "/lesson_three/pronouns/page_twenty",
                                                                       "back": "/lesson_three/pronouns/page_eighteen",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat",
                                                                       "title": "Pronouns",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def pronouns_page_twenty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twenty.html", {"next": "/lesson_three/pronouns/page_twentyone",
                                                                     "back": "/lesson_three/pronouns/page_nineteen",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def pronouns_page_twentyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentyone.html", {"next": "/lesson_three/pronouns/page_twentytwo",
                                                                        "back": "/lesson_three/pronouns/page_twenty",
                                                                        "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 3: Let's Eat",
                                                                        "title": "Pronouns",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def pronouns_page_twentytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentytwo.html",
                      {"next": "/lesson_three/pronouns/page_twentythree",
                       "back": "/lesson_three/pronouns/page_twentyone",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_twentythree(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentythree.html",
                      {"next": "/lesson_three/pronouns/page_twentyfour",
                       "back": "/lesson_three/pronouns/page_twentytwo",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_twentyfour(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentyfour.html",
                      {"next": "/lesson_three/pronouns/page_twentyfive",
                       "back": "/lesson_three/pronouns/page_twentythree",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_twentyfive(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentyfive.html",
                      {"next": "/lesson_three/pronouns/page_twentysix",
                       "back": "/lesson_three/pronouns/page_twentyfour",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_twentysix(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentysix.html",
                      {"next": "/lesson_three/pronouns/page_twentyseven",
                       "back": "/lesson_three/pronouns/page_twentyfive",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_twentyseven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentyseven.html",
                      {"next": "/lesson_three/pronouns/page_twentyeight",
                       "back": "/lesson_three/pronouns/page_twentysix",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_twentyeight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentyeight.html",
                      {"next": "/lesson_three/pronouns/page_twentynine",
                       "back": "/lesson_three/pronouns/page_twentyseven",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_twentynine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_twentynine.html",
                      {"next": "/lesson_three/pronouns/page_thirty",
                       "back": "/lesson_three/pronouns/page_twentyeight",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_thirty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_thirty.html",
                      {"next": "/lesson_three/pronouns/page_thirtyone",
                       "back": "/lesson_three/pronouns/page_twentynine",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_thirtyone(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_thirtyone.html",
                      {"next": "/lesson_three/pronouns/page_thirtytwo",
                       "back": "/lesson_three/pronouns/page_thirty",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_thirtytwo(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_thirtytwo.html",
                      {"next": "/lesson_three/pronouns/page_thirythree",
                       "back": "/lesson_three/pronouns/page_thirtyone",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_thirtythree(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_thirtythree.html",
                      {"next": "/lesson_three/pronouns/page_thirtyfour",
                       "back": "/lesson_three/pronouns/page_thirtytwo",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_thirtyfour(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_thirtytwo.html",
                      {"next": "/lesson_three/page_one/page_thirtyfive",
                       "back": "/lesson_three/pronouns/page_thirtythree",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def pronouns_page_thirtyfive(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/pronouns/page_thirtytwo.html",
                      {"next": "/lesson_three/house/page_one",
                       "back": "/lesson_three/pronouns/page_thirtyfour",
                       "solved": solution.solved,
                       "lessons": lessons,
                       "lesson": "Unit 3: Let's Eat",
                       "title": "Pronouns",
                       "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def house_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_one.html", {"next": "/lesson_three/house/page_two",
                                                               "back": "/lesson_three/house/page_one",
                                                               "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "picture": "svg/lesson3/house/bedroom 01.svg",
                                                               "lesson": "Unit 3: Let's Eat", "title": "House",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def house_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_two.html", {"next": "/lesson_three/house/page_three",
                                                               "back": "/lesson_three/house/page_one",
                                                               "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "picture": "svg/lesson3/house/bathroom 01.svg",
                                                               "lesson": "Unit 3: Let's Eat", "title": "House",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def house_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_three.html", {"next": "/lesson_three/house/page_four",
                                                                 "back": "/lesson_three/house/page_two",
                                                                 "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "picture": "svg/lesson3/house/living room 01.svg",
                                                                 "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def house_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_four.html", {"next": "/lesson_three/house/page_five",
                                                                "back": "/lesson_three/house/page_three",
                                                                "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "picture": "svg/lesson3/house/kitchen 01.svg",
                                                                "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def house_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_five.html", {"next": "/lesson_three/house/page_six",
                                                                "back": "/lesson_three/house/page_four",
                                                                "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "picture": "svg/lesson3/house/dining room 01.svg",
                                                                "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def house_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_six.html", {"next": "/lesson_three/house/page_seven",
                                                               "back": "/lesson_three/house/page_five",
                                                               "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "picture": "svg/lesson3/house/garden 01.svg",
                                                               "lesson": "Unit 3: Let's Eat", "title": "House",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def house_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_seven.html", {"next": "/lesson_three/house/page_eight",
                                                                 "back": "/lesson_three/house/page_six",
                                                                 "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "picture": "svg/lesson3/house/garden 01.svg",
                                                                 "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def house_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_eight.html", {"next": "/lesson_three/house/page_nine",
                                                                 "back": "/lesson_three/house/page_seven",
                                                                 "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "picture": "svg/lesson3/house/garden 01.svg",
                                                                 "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def house_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_nine.html", {"next": "/lesson_three/house/page_ten",
                                                                "back": "/lesson_three/house/page_eight",
                                                                "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "picture": "svg/lesson3/house/garden 01.svg",
                                                                "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })


def house_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_six.html", {"next": "/lesson_three/house/page_seven",
                                                               "back": "/lesson_three/house/page_five",
                                                               "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "picture": "svg/lesson3/house/garden 01.svg",
                                                               "lesson": "Unit 3: Let's Eat", "title": "House",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def house_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_ten.html", {"next": "/lesson_three/house/page_eleven",
                                                               "back": "/lesson_three/house/page_nine",
                                                               "solved": solution.solved,
                                                               "lessons": lessons,
                                                               "picture": "svg/lesson3/house/garden 01.svg",
                                                               "lesson": "Unit 3: Let's Eat", "title": "House",
                                                               "user": request.session['user'],
                                                               "src": src_ref, "parts": parts, "colors": colors
                                                               })


def house_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_eleven.html", {"next": "/lesson_three/house/page_twelve",
                                                                 "back": "/lesson_three/house/page_ten",
                                                                 "solved": solution.solved,
                                                                 "lessons": lessons,
                                                                 "picture": "svg/lesson3/house/garden 01.svg",
                                                                 "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                 "user": request.session['user'],
                                                                 "src": src_ref, "parts": parts, "colors": colors
                                                                 })


def house_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_twelve.html", {"next": "/lesson_three/house/page_thirteen",
                                                                  "back": "/lesson_three/house/page_elven",
                                                                  "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "picture": "svg/lesson3/house/garden 01.svg",
                                                                  "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def house_page_thirteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_thirteen.html", {"next": "/lesson_three/house/page_fourteen",
                                                                    "back": "/lesson_three/house/page_twelve",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "picture": "svg/lesson3/house/garden 01.svg",
                                                                    "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def house_page_fourteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_fourteen.html", {"next": "/lesson_three/house/page_fifteen",
                                                                    "back": "/lesson_three/house/page_fourteen",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "picture": "svg/lesson3/house/garden 01.svg",
                                                                    "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def house_page_fifteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_fifteen.html", {"next": "/lesson_three/house/page_sixteen",
                                                                   "back": "/lesson_three/house/page_fourteen",
                                                                   "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "picture": "svg/lesson3/house/garden 01.svg",
                                                                   "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def house_page_sixteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_sixteen.html", {"next": "/lesson_three/house/page_seventeen",
                                                                   "back": "/lesson_three/house/page_fifteen",
                                                                   "solved": solution.solved,
                                                                   "lessons": lessons,
                                                                   "picture": "svg/lesson3/house/garden 01.svg",
                                                                   "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                   "user": request.session['user'],
                                                                   "src": src_ref, "parts": parts, "colors": colors
                                                                   })


def house_page_seventeen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_seventeen.html", {"next": "/lesson_three/house/page_eighteen",
                                                                     "back": "/lesson_three/house/page_sixteen",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "picture": "svg/lesson3/house/garden 01.svg",
                                                                     "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def house_page_eighteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_eighteen.html", {"next": "/lesson_three/house/page_nineteen",
                                                                    "back": "/lesson_three/house/page_seventeen",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "picture": "svg/lesson3/house/garden 01.svg",
                                                                    "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def house_page_nineteen(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_nineteen.html", {"next": "/lesson_three/house/page_twenty",
                                                                    "back": "/lesson_three/house/page_six",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "picture": "svg/lesson3/house/garden 01.svg",
                                                                    "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


def house_page_twenty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_twenty.html", {"next": "/lesson_three/house/page_twenty",
                                                                  "back": "/lesson_three/house/page_nineteen",
                                                                  "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "picture": "svg/lesson3/house/garden 01.svg",
                                                                  "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def house_page_twenty(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/house/page_twenty.html", {"next": "/lesson_three/house/page_twenty",
                                                                  "back": "/lesson_three/house/page_nineteen",
                                                                  "solved": solution.solved,
                                                                  "lessons": lessons,
                                                                  "picture": "svg/lesson3/house/garden 01.svg",
                                                                  "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                  "user": request.session['user'],
                                                                  "src": src_ref, "parts": parts, "colors": colors
                                                                  })


def modal_verbs_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_one.html", {"next": "/lesson_three/modal_verbs/page_two",
                                                                     "back": "/lesson_three/modal_verbs/page_one",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 3: Let's Eat",
                                                                     "title": "Modal Verbs",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def modal_verbs_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_two.html", {"next": "/lesson_three/modal_verbs/page_three",
                                                                     "back": "/lesson_three/modal_verbs/page_one",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 3: Let's Eat",
                                                                     "title": "Modal Verbs",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def modal_verbs_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_three.html", {"next": "/lesson_three/modal_verbs/page_four",
                                                                       "back": "/lesson_three/modal_verbs/page_two",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat",
                                                                       "title": "Modal Verbs",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def modal_verbs_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_four.html", {"next": "/lesson_three/modal_verbs/page_five",
                                                                      "back": "/lesson_three/modal_verbs/page_three",
                                                                      "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 3: Let's Eat",
                                                                      "title": "Modal Verbs",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts,
                                                                      "colors": colors
                                                                      })


def modal_verbs_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_five.html", {"next": "/lesson_three/modal_verbs/page_six",
                                                                      "back": "/lesson_three/modal_verbs/page_four",
                                                                      "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 3: Let's Eat",
                                                                      "title": "Modal Verbs",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors
                                                                      })


def modal_verbs_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_six.html", {"next": "/lesson_three/modal_verbs/page_seven",
                                                                     "back": "/lesson_three/modal_verbs/page_five",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 3: Let's Eat",
                                                                     "title": "Modal Verbs",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts,
                                                                     "colors": colors
                                                                     })


def modal_verbs_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_seven.html", {"next": "/lesson_three/modal_verbs/page_eight",
                                                                       "back": "/lesson_three/modal_verbs/page_six",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat",
                                                                       "title": "Modal Verbs",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def modal_verbs_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_eight.html", {"next": "/lesson_three/modal_verbs/page_nine",
                                                                       "back": "/lesson_three/modal_verbs/page_nine",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat",
                                                                       "title": "Modal Verbs",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts,
                                                                       "colors": colors
                                                                       })


def modal_verbs_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_nine.html", {"next": "/lesson_three/modal_verbs/page_ten",
                                                                      "back": "/lesson_three/modal_verbs/page_eight",
                                                                      "solved": solution.solved,
                                                                      "lessons": lessons,
                                                                      "lesson": "Unit 3: Let's Eat",
                                                                      "title": "Modal Verbs",
                                                                      "user": request.session['user'],
                                                                      "src": src_ref, "parts": parts, "colors": colors
                                                                      })


def modal_verbs_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_ten.html", {"next": "/lesson_three/modal_verbs/page_eleven",
                                                                     "back": "/lesson_three/modal_verbs/page_nine",
                                                                     "solved": solution.solved,
                                                                     "lessons": lessons,
                                                                     "lesson": "Unit 3: Let's Eat",
                                                                     "title": "Modal Verbs",
                                                                     "user": request.session['user'],
                                                                     "src": src_ref, "parts": parts, "colors": colors
                                                                     })


def modal_verbs_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_eleven.html", {"next": "/lesson_three/modal_verbs/page_twelve",
                                                                        "back": "/lesson_three/modal_verbs/page_ten",
                                                                        "solved": solution.solved,
                                                                        "lessons": lessons,
                                                                        "lesson": "Unit 3: Let's Eat",
                                                                        "title": "Modal Verbs",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def modal_verbs_page_twelve(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/modal_verbs/page_welve.html", {"next": "/lesson_three/modal_verbs/page_twelve",
                                                                       "back": "/lesson_three/modal_verbs/page_eleven",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "House",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def market_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_one.html", {"next": "/lesson_three/market/page_two",
                                                                       "back": "/lesson_three/modal_verbs/page_twelve",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })

def market_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_two.html", {"next": "/lesson_three/market/page_three",
                                                                       "back": "/lesson_three/market/page_one",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def market_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_three.html", {"next": "/lesson_three/market/page_four",
                                                                       "back": "/lesson_three/market/page_two",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })

def market_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_four.html", {"next": "/lesson_three/market/page_five",
                                                                       "back": "/lesson_three/market/page_three",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def market_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_five.html", {"next": "/lesson_three/market/page_six",
                                                                       "back": "/lesson_three/market/page_four",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def market_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_six.html", {"next": "/lesson_three/market/page_seven",
                                                                       "back": "/lesson_three/market/page_five",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })

def market_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_seven.html", {"next": "/lesson_three/market/page_eight",
                                                                       "back": "/lesson_three/market/page_six",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })

def market_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_eight.html", {"next": "/lesson_three/market/page_nine",
                                                                       "back": "/lesson_three/market/page_seven",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def market_page_nine(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_nine.html", {"next": "/lesson_three/market/page_ten",
                                                                       "back": "/lesson_three/market/page_eight",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })

def market_page_ten(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_ten.html", {"next": "/lesson_three/market/page_eleven",
                                                                       "back": "/lesson_three/market/page_nine",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def market_page_eleven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/market/page_eleven.html", {"next": "/lesson_three/city/page_one",
                                                                       "back": "/lesson_three/market/page_ten",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def city_page_one(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_one.html", {"next": "/lesson_three/city/page_two",
                                                                       "back": "/lesson_three/market/page_eleven",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })


def city_page_two(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_two.html", {"next": "/lesson_three/city/page_three",
                                                                       "back": "/lesson_three/city/page_one",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })

def city_page_three(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_three.html", {"next": "/lesson_three/city/page_four",
                                                                       "back": "/lesson_three/city/page_two",
                                                                       "solved": solution.solved,
                                                                       "lessons": lessons,
                                                                       "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                       "user": request.session['user'],
                                                                       "src": src_ref, "parts": parts, "colors": colors
                                                                       })

def city_page_four(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_four.html", {"next": "/lesson_three/city/page_five",
                                                                "back": "/lesson_three/city/page_three",
                                                                "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })

def city_page_five(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_five.html", {"next": "/lesson_three/city/page_six",
                                                                "back": "/lesson_three/city/page_four",
                                                                "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })

def city_page_six(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_six.html", {"next": "/lesson_three/city/page_seven",
                                                                "back": "/lesson_three/city/page_five",
                                                                "solved": solution.solved,
                                                                "lessons": lessons,
                                                                "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                                "user": request.session['user'],
                                                                "src": src_ref, "parts": parts, "colors": colors
                                                                })

def city_page_seven(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_seven.html", {"next": "/lesson_three/city/page_eight",
                                                              "back": "/lesson_three/city/page_six",
                                                              "solved": solution.solved,
                                                              "lessons": lessons,
                                                              "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                              "user": request.session['user'],
                                                              "src": src_ref, "parts": parts, "colors": colors
                                                              })

def city_page_eight(request):
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        solution = get_or_create_solution(user, request.path)
        return render(request, "lesson3/city/page_eight.html", {"next": "/lesson_three/city/page_nine",
                                                              "back": "/lesson_three/city/page_seven",
                                                              "solved": solution.solved,
                                                              "lessons": lessons,
                                                              "lesson": "Unit 3: Let's Eat", "title": "At the store",
                                                              "user": request.session['user'],
                                                              "src": src_ref, "parts": parts, "colors": colors
                                                              })



def pictures(request):
    sentences = {"sun.svg": "I get up.", "brush.svg": "I brush my teeth.",
                 "hairbrush.svg": "I comb my hair.", "shirt.svg": "I get dressed.",
                 "meal0.svg": "I have breakfast.", "newspaper.svg": "I read the newspaper.",
                 "car0.svg": "I go to work.", "papers.svg": "I work.",
                 "apple.svg": "I eat a snack.", "car1.svg": "I arrive home.",
                 "pot.svg": "I make lunch.", "meal1.svg": "I have lunch.",
                 "dishes.svg": "I do the dishes.", "shower.svg": "I take a shower.", "tv.svg": "I watch TV.",
                 "book.svg": "I read a book.",
                 "meal2.svg": "I have dinner.", "night.svg": "I go to bed."
                 }
    count = {"meal.svg": 0, "car.svg": 0}
    img = {}
    for image in os.listdir("ucbenik/static/svg/lesson2/daily_routines"):
        if image == "meal.svg" or image == "car.svg":
            img["svg/lesson2/daily_routines/" + str(image.split(".")[0]) + str(count[image]) + ".svg"] = sentences[
                str(image.split(".")[0]) + str(count[image]) + ".svg"]
            count[image] += 1
        else:
            img["svg/lesson2/daily_routines/" + str(image)] = sentences[image]
    return JsonResponse({"links": img})


def glossary(request):
    if request.get_full_path().split("/")[2] == "introduction":
        return JsonResponse({"vocabulary": {"hello": "živijo", "name": "ime", "nickname": "vzdevek", "age": "starost",
                                            "country": "država",
                                            "I": "jaz", "you": "ti", "yes": "ja", "no": "ne", "my": "moj",
                                            "your": "tvoj", "year": "leto", "old": "star",
                                            "born": "rojen", "to live": "živeti", "Slovenia": "Slovenija", "who": "kdo",
                                            "what": "kaj", "where": "kje",
                                            "how": "kako", "person": "oseba", "notebook": "zvezek"}
                             })
    elif request.get_full_path().split("/")[2] == "character_select":
        return JsonResponse({"vocabulary": {"to choose": "izbrati", "skin": "koža", "colour": "barva", "tall": "visok",
                                            "short": "nizek, kratek",
                                            "plump": "močnejše postave", "slender": "vitek", "hair": "lasje",
                                            "long": "dolg", "brown": "rjava",
                                            "beard": "brada", "mustache": "brki", "to wear": "nositi",
                                            "glasses": "očala", "to pick": "izbrati",
                                            "clothes": "oblačila"},
                             "additional": {"fat": "debel", "thin": "suh", "slim": "vitek"}
                             })
    elif request.get_full_path().split("/")[2] == "numbers":
        return JsonResponse({"vocabulary": {"number": "število", "to count": "šteti", "zero": "nič", "one": "ena",
                                            "two": "dve", "three": "tri",
                                            "four": "štiri", "five": "pet", "six": "šest", "seven": "sedem",
                                            "eight": "osem", "nine": "devet",
                                            "ten": "deset", "eleven": "enajst", "twelve": "dvanajst",
                                            "thirteen": "trinjast", "fourteen": "štirinajst",
                                            "fifteen": "petnajst", "sixteen": "šestnajst", "seventeen": "sedemnajst",
                                            "eighteen": "osemnajst",
                                            "nineteen": "devetnajst", "twenty": "dvajset", "twenty-one": "enaindvajset",
                                            "thirty": "trideset",
                                            "forty": "štirideset", "fifty": "petedeset", "sixty": "šestdeset",
                                            "seventy": "sedemdeset",
                                            "eighty": "osemdeset", "ninety": "devetdeset", "hundred": "sto",
                                            "thousand": "tisoč", "million": "million"},
                             "additional": {"ordinal number": "vrstilni števnik", "first": "prvi", "second": "drugi",
                                            "third": "tretji", "fourth": "četrti", "fifth": "peti", "sixth": "šesti",
                                            "seventh": "sedmi",
                                            "eighth": "osmi", "ninth": "deveti", "tenth": "deseti"}
                             }
                            )
    elif request.get_full_path().split("/")[2] == "colors":
        return JsonResponse(
            {"vocabulary": {"to look": "gledati", "colour": "barva", "to click": "klikati", "word": "beseda",
                            "to listen": "poslušati", "to repeat": "ponoviti", "red": "rdeča", "orange": "oranžna",
                            "yellow": "rumena", "green": "zelena", "blue": "modra", "purple": "vijolična",
                            "pink": "roza",
                            "black": "črna", "grey": "siva", "white": "bela", "brown": "rjava", "gold": "zlata",
                            "silver": "srebrna"},
             "additional": {"shade": "odtenek", "adjective": "pridevnik", "light": "svetel", "dark": "temen",
                            "bright": "živ"}
             })
    elif request.get_full_path().split("/")[2] == "years":
        return JsonResponse(
            {"vocabulary": {"year": "leto", "to learn": "učiti se", "to pronounce": "izgovoriti", "correct": "pravilen",
                            "and": "in", "in": "v", "to read": "brati", "to say": "reči", "to hear": "slišati"},
             "rules": {
                 "rule1": "Pred letnicami uporabljamo predlog IN, ki pomeni V.",
                 "rule2": "Če sprašujemo po letnici, uporabimo vprašalnico WHAT YEAR."
             }
             })
    elif request.get_full_path().split("/")[2] == "personal_traits":
        return JsonResponse(
            {"vocabulary": {"personality": "osebnost", "trait": "lastnost, značilnost", "short": "nizek, kratek",
                            "plump": "močnejše postave", "smart": "pameten", "stupid": "neumen", "good": "dober",
                            "bad": "slab",
                            "hard-working": "delaven", "lazy": "len", "generous": "radodaren, velikodušen",
                            "selfish": "sebičen",
                            "kind": "prijazen", "mean": "neprijazen, nesramen", "funny": "zabaven",
                            "boring": "dolgočasen",
                            "outgoing": "družaben", "shy": "sramežljiv", "reliable": "zanesljiv",
                            "unreliable": "nezanesljiv",
                            "opposite": "nasprotje", "to describe": "opisati", "to try": "poskusiti",
                            "to ask": "vprašati",
                            "awesome": "super", "surprise": "presenečenje", "to meet": "spoznati",
                            "friend": "prijatelj",
                            "translation": "prevod"}
             })
    elif request.get_full_path().split("/")[2] == "he_she_it":
        return JsonResponse(
            {"vocabulary": {"I": "jaz", "you (ed.)": "ti", "he": "on", "she": "ona", "it": "ono", "we": "mi",
                            "you (mn.)": "vi", "they": "oni", "to be": "biti", "to talk": "govoriti",
                            "people": "ljudje",
                            "to use": "uporabiti", "to check": "preveriti", "to complete": "zaključiti",
                            "pronoun": "zaimek",
                            "knowledge": "znanje", "happy": "srečen", "sad": "žalosten", "bald": "plešast",
                            "sentence": "poved",
                            "form": "oblika", "text": "besedilo", "question": "vprašanje", "answer": "odgovor",
                            "affirmative": "trdilen",
                            "negative": "nikalen", "to have": "imeti", "singular": "ednina",
                            "plural": "množina", "verb": "glagol", "true": "resničen, pravilen", "false": "napačen"},
             "rules": {
                 "rule1": "Ko govorimo o nekom v tretji osebi, uporabljamo zaimka HE in SHE – odvisno od spola osebe. SHE uporabljamo, ko govorimo o osebi ženskega spola. HE "
                          "uporabljamo, ko govorimo o osebi moškega spola. IT pa uporabljamo, ko govorimo o živalih, predmetih, … IZJEMA: Če govorimo o hišnih  ljubljenčkih, "
                          "le redko uporabimo IT, saj poznamo spol in ime živali.",
                 "rule2": "Namesto zaimkov lahko uporabimo tudi osebna imena. Prav tako lahko osebna imena zamenjamo z zaimki.",
                 "rule3": "Okrajšano glagolsko obliko lahko uporabljamo tudi ob osebnih imenih ali predmetih, ne le ob osebnih zaimkih.",
                 "rule4": "Osnovna vprašanja vedno tvorimo s pomočjo TRDILNE OBLIKE. Torej IS HE HAPPY? in ne ISN'T HAPPY?. Glagol je v vprašanju vedno v trdilni obliki."
             }
             })
    elif request.get_full_path().split("/")[2] == "day_week_month":
        return JsonResponse({"vocabulary": {'Monday': 'ponedeljek', 'Tuesday': 'torek', 'Wednesday': 'sreda',
                                            'Thursday': 'četrtek', 'Friday': 'petek',
                                            'Saturday': 'sobota', 'Sunday': 'nedelja', 'January': 'januar',
                                            'February': 'februar', 'March': 'marec',
                                            'April': 'april', 'May': 'maj', 'June': 'junij', 'July': 'julij',
                                            'August': 'avgust', 'September': 'september', 'October': 'oktober',
                                            'November': 'november', 'December': 'december', 'day': 'dan',
                                            'week': 'teden', 'month': 'mesec', 'English': 'angleščina',
                                            'capitalised': 'z veliko začetnico', 'sun': 'sonce', 'sunny': 'sončno',
                                            'again': 'spet', 'to see': 'videti', 'to remember': 'spomniti se',
                                            'to start': 'začeti', 'careful': 'previden', 'because': 'ker',
                                            'letter': 'črka', 'difference': 'razlika', 'weekend': 'vikend',
                                            'free': 'svoboden'
                                            }})
    elif request.get_full_path().split("/")[2] == "articles":
        return JsonResponse({"vocabulary": {'a': 'nedoločni člen', 'an': 'nedoločni člen', 'the': 'določni člen',
                                            'apple': 'jabolko', 'table': 'miza', 'book': 'knjiga', 'house': 'hiša',
                                            'TV': 'televizija', 'to turn on': 'prižgati', 'to want': 'želeti',
                                            'to watch': 'gledati', 'film': 'film', 'queen': 'kraljica',
                                            'drink': 'pijača',
                                            'university': 'univerza', 'doctor': 'zdravnik', 'engineer': 'inženir',
                                            'toilet': 'stranišče', 'sister': 'sestra', 'bus driver': 'voznik avtobusa',
                                            'teacher': 'učitelj', 'balloon': 'balon', 'honest': 'iskren', 'owl': 'sova',
                                            'country': 'država', 'ice-cream': 'sladoled', 'to add': 'dodati',
                                            'salt': 'sol', 'to drink': 'piti', 'water': 'voda',
                                            'to need': 'potrebovati', 'information': 'informacije', 'love': 'ljubezen',
                                            'tomorrow': 'jutri',
                                            'to celebrate': 'praznovati', 'Christmas': 'Božič', 'artist': 'umetnik',
                                            'birthday': 'rojstni dan', 'school': 'šola', 'Ester': 'velika noč',
                                            'luck': 'sreča', 'death': 'smrt', 'difficult': 'težaven', 'topic': 'tema',
                                            'to give': 'dati', 'chance': 'priložnost', 'thief': 'tat',
                                            'shirt': 'majica',
                                            'cat': 'mačka', 'big': 'velik', 'pretty': 'lep', 'to play': 'igrati',
                                            'piano': 'klavir', 'to climb': 'plezati', 'river': 'reka', 'ocean': 'ocean',
                                            'north': 'sever', 'south': 'jug', 'east': 'vzhod', 'west': 'zahod',
                                            'basketball': 'košarka', 'maths': 'matematika', 'to speak': 'govoriti',
                                            'breakfast': 'zajtrk', 'beautiful': 'prelep', 'capital': 'glavno mesto',
                                            'violin': 'violina', 'to close': 'zapreti', 'window': 'okno',
                                            'to borrow': 'sposoditi si', 'pencil': 'svinčnik', 'world': 'svet',
                                            'city': 'mesto', 'writer': 'pisatelj', 'to go': 'iti', 'France': 'Francija',
                                            'cello': 'violončelo', 'baseball': 'bejzbol', 'library': 'knjižnica',
                                            'mom': 'mati', 'to make': 'narediti', 'lunch': 'kosilo',
                                            'hard': 'trd, težaven',
                                            'flower': 'roža', 'dog': 'pes', 'bus': 'avtobus', 'kiss': 'poljub',
                                            'church': 'cerkev', 'brush': 'krtača', 'box': 'škatla',
                                            'tomato': 'paradižnik',
                                            'family': 'družina', 'lady': 'gospa', 'baby': 'dojenček', 'story': 'zgodba',
                                            'play': 'igra', 'way': 'pot, način', 'boy': 'fant', 'monkey': 'opica',
                                            'knife': 'nož', 'wife': 'žena', 'scarf': 'šal', 'child': 'otrok',
                                            'woman': 'ženska', 'man': 'moški', 'person': 'oseba', 'tooth': 'zob',
                                            'foot': 'del noge od gležnja nižje', 'mouse': 'miš', 'fish': 'riba',
                                            'deer': 'srnja', 'sheep': 'ovca', 'noun': 'samostalnik',
                                            'orange': 'pomaranča',
                                            'strawberry': 'jagoda', 'photo': 'fotografija', 'dress': 'obleka',
                                            'key': 'ključ', 'avocado': 'avokado', 'enemy': 'sovražnik',
                                            'bench': 'klopca',
                                            'guy': 'moški', 'toy': 'igrača', 'zoo': 'živalski vrt',
                                            'kite': '(papirnati) zmaj', 'daisy': 'marjetica', 'echo': 'odmev',
                                            'army': 'vojska',
                                            'potato': 'krompir', 'class': 'razred', 'hero': 'junak', 'radio': 'radio',
                                            'road': 'cesta', 'glass': 'steklo, kozarec', 'cloud': 'oblak',
                                            'puffy': 'napihnjen', 'fresh': 'svež', 'dirty': 'umazan',
                                            'naughty': 'poreden', 'sad': 'žalosten', 'rose': 'vrtnica', 'nose': 'nos',
                                            'fly': 'muha',
                                            'annoying': 'nadležen', 'donkey': 'osel', 'loud': 'glasen',
                                            'address': 'naslov', 'sweet': 'sladek', 'spy': 'vohun', 'smart': 'pameten',
                                            'princess': 'princesa', 'watch': '(ročna) ura', 'wrong': 'napačen',
                                            'quiet': 'tih', 'glasses': 'očala', 'tree': 'drevo', 'huge': 'ogromen',
                                            'wool': 'volna',
                                            'cross': 'križ', 'wall': 'stena', 'bush': 'grm', 'crayon': 'voščenka',
                                            'ring': 'prstan', 'classmate': 'sošolec, sošolka', 'bracelet': 'zapestnica',
                                            'desk': '(šolska) klop', 'chair': 'stol', 'pen': 'kemični svinčnik',
                                            'slipper': 'copat'}})
    elif request.get_full_path().split("/")[2] == "family":
        return JsonResponse({"vocabulary": {'family': 'družina', 'member': 'član', 'to tell': 'povedati',
                                            'something': 'nekaj', 'important': 'pomemben', 'birthday': 'rojstni dan',
                                            'to visit': 'obiskati', 'afternoon': 'popoldan', 'to have': 'imeti',
                                            'husband': 'mož', 'wife': 'žena', 'son': 'sin', 'daughter': 'hčerka',
                                            'parents': 'starši', 'mother': 'mama', 'father': 'oče', 'this': 'to',
                                            'sentence': 'stavek', 'cat': 'mačka', 'toy': 'igrača', 'house': 'hiša',
                                            'description': 'opis', 'ago': 'pred, nazaj', 'kids': 'otroci',
                                            'countryside': 'podeželje', 'baby': 'dojenček', 'with': 's/z',
                                            'to miss': 'pogrešati',
                                            'friend': 'prijatelj', 'own': 'lasten', 'university': 'univerza',
                                            'work': 'delo', 'daughter-in-law': 'snaha', 'son-in-law': 'zet',
                                            'sister-in-law': 'svakinja', 'brother-in-law': 'svak', 'rest': 'preostanek',
                                            'grandchild': 'vnuk, vnukinja', 'grandchildren': 'vnuki',
                                            'grandson': 'vnuk',
                                            'granddaughter': 'vnukinja', 'second': 'drugi', 'once': 'enkrat',
                                            'dinner': 'večerja', 'to grow up': 'odraščati', 'fast': 'hiter/hitro',
                                            'soon': 'kmalu',
                                            'great-grandmother': 'prababica', 'great-grandfather': 'praded',
                                            'great-grandparents': 'prababica in pradedek', 'tree': 'drevo',
                                            'family tree': 'družinsko drevo', '(family) relation': '(družinska) vez',
                                            'different': 'drugačen', 'to divorce': 'ločiti se', 'first': 'prvi',
                                            'to marry': 'poročiti se', 'to bring': 'prinesti', 'stepson': 'pastorek',
                                            'stepfather': 'očim', 'stepdaughter': 'pastorka', 'stepmother': 'mačeha',
                                            'to describe': 'opisati', 'to form': 'tvoriti', 'about': 'o'}})
    elif request.get_full_path().split("/")[2] == "clothes":
        return JsonResponse({"vocabulary": {'clothes': 'oblačila', 'today': 'danes',
                                            'to come over': 'obiskati/priti na obisk', 'to help': 'pomagati',
                                            'to decide': 'odločiti se',
                                            'to wear': 'nositi (oblačila)', 'to open': 'odpreti', 'wardrobe': 'omara',
                                            'blouse': 'bluza', 'restaurant': 'restavracija', 'pants': 'hlače',
                                            'to look': 'izgledati', 'casual': 'neformalen, sproščen', 'dress': 'obleka',
                                            'to dance': 'plesati', 'shoes': 'čevlji', 'occasion': 'priložnost',
                                            'T-shirt': 'majica s kratkimi rokavi', 'to hike': 'hoditi', 'hike': 'pohod',
                                            'skirt': 'krilo', 'socks': 'nogavice', 'feet': 'stopala',
                                            'to be cold': 'zebsti', 'shorts': 'kratke hlače', 'summer': 'poletje',
                                            'boots': 'škornji', 'to rain': 'deževati', 'rain': 'dež', 'coat': 'plašč',
                                            'cold': 'mrzlo/mrzel', 'gloves': 'rokavice', 'to snow': 'snežiti',
                                            'snow': 'sneg', 'scarf': 'šal', 'neck': 'vrat', 'to protect': 'ščititi',
                                            'to protect from': 'ščititi pred', 'wind': 'veter', 'swimsuit': 'kopalke',
                                            'beach': 'plaža', 'jacket': 'jakna', 'outside': 'zunaj',
                                            'trainers': 'športni copati', '“to run”': '“teči”', '“hat”': 'klobuk',
                                            'ears': 'ušesa', 'tie': 'kravata', 'formally': 'formalno', 'suit': 'obleka',
                                            'wedding': 'poroka', 'sweater': 'pulover', 'winter': 'zima',
                                            'jeans': 'kavbojke', 'walk': '  sprehod', 'to walk': 'hoditi',
                                            'piece': 'kos',
                                            'autumn': 'jesen', 'spring': 'pomlad', 'windy': 'vetrovno', 'when': 'ko'}})
    elif request.get_full_path().split("/")[2] == "time":
        return JsonResponse({"vocabulary": {'What time is it?': 'Koliko je ura?', 'hour': 'ura', 'a.m.': 'dopoldan',
                                            'p.m.': 'popoldan', 'midnight': 'polnoč', 'noon': 'poldan',
                                            'morning': 'jutro',
                                            'day': 'dan', 'afternoon': 'popoldne', 'night': 'noč', 'clock': 'ura',
                                            'quarter': 'četrt', 'past': 'čez', 'to': 'do', 'half': 'pol'}})
    elif request.get_full_path().split("/")[2] == "present_simple" or request.get_full_path().split("/")[
        2] == "daily_routines":
        return JsonResponse({"vocabulary": {'grammar': 'slovnica', 'present': 'sedanjost', 'routine': 'rutina',
                                            'habit': 'navada', 'everyday (adj.)': 'vsakodnevni',
                                            'activity': 'aktivnost',
                                            'state': 'stanje', 'general': 'splošen', 'truth': 'resnica', 'tense': 'čas',
                                            'never': 'nikoli', 'school': 'šola', 'milk': 'mleko', 'to drink': 'piti',
                                            'flower': 'roža', 'to breath': 'dihati', 'nose': 'nos', 'through': 'skozi',
                                            'person': 'oseba', 'verb': 'glagol', 'to drive': 'voziti', 'car': 'avto',
                                            'work': 'delo/služba', 'always': 'vedno', 'sometimes': 'včasih',
                                            'often': 'pogosto', 'rarely': 'redko', 'usually': 'običajno',
                                            'every day': 'vsak dan',
                                            'every week': 'vsak teden', 'to add': 'dodati', 'careful': 'previden',
                                            'to end': 'končati', 'suffix': 'končnica', 'to pronounce': 'izgovoriti',
                                            'example': 'primer', 'to kiss': 'poljubiti', 'kiss': 'poljub',
                                            'to brush': 'krtačiti', 'teeth': 'zobje', 'to go': 'iti',
                                            'to watch': 'gledati',
                                            'TV': 'televizija', 'to miss': 'pogrešati', 'consonant': 'soglasnik',
                                            'third': 'tretji', 'to cry': 'jokati', 'to punch': 'udariti',
                                            'vowel': 'samoglasnik',
                                            'violin': 'violina', 'piano': 'klavir', 'to enjoy': 'uživati',
                                            'to read': 'brati', 'to fly': 'leteti', 'kite': '(papirnati) zmaj',
                                            'to fly a kite': 'spuščati zmaja', 'to party': 'zabavati se',
                                            'weekend': 'vikend', 'negative sentence': 'nikalna poved',
                                            'structure': 'struktura',
                                            'before': 'pred', 'short': 'kratek, nizek', 'shorter': 'krajši',
                                            'singular': 'ednina', 'to eat': 'jesti', 'meat': 'meso', 'word': 'beseda',
                                            'to use': 'uporabiti', 'to like': 'imeti rad', 'animal': 'žival',
                                            'to love': 'ljubiti', 'parents': 'starši', 'to listen': 'poslušati',
                                            'music': 'glasba',
                                            'to play': 'igrati', 'guitar': 'kitara', 'cat': 'mačka',
                                            'to sleep': 'spati', 'lunch': 'kosilo', 'together': 'skupaj',
                                            'to write': 'pisati',
                                            "children's book": 'knjiga za otroke', 'to sing': 'peti',
                                            'band': 'glasbena skupina”', 'exception': 'izjema', 'wrong': 'napačen',
                                            'order': '(vrstni) red',
                                            'form': 'oblika', 'to answer': 'odgovoriti', 'football': 'ameriški nogomet',
                                            'young': 'mlad', 'chess': 'šah', 'to cook': 'kuhati', 'dog': 'pes',
                                            'alone': 'sam', 'to talk': 'govoriti', 'to draw': 'risati',
                                            'to live': 'živeti', 'apartment': 'stanovanje', 'to hate': 'sovražiti',
                                            'from': 'od',
                                            'late': 'pozen', 'lost': 'izgubljen', 'to forget': 'pozabiti',
                                            'common': 'običajno', 'to work out': 'telovaditi', 'to clean': 'čistiti',
                                            'coffee': 'kava',
                                            'garden': 'vrt', 'board games': 'družabne igre',
                                            'to take a shower': '(s)tuširati se', 'shower': 'tuš', 'sleep': 'spanje',
                                            'beach': 'plaža',
                                            'restaurant': 'restavracija', 'nap': 'dremež', 'walk': 'sprehod',
                                            'cards': 'karte', 'computer': 'računalnik', 'gym': 'telovadnica',
                                            'to paint': 'slikati',
                                            'shopping': 'nakupovanje', 'to feed': 'hraniti'}})
    elif request.get_full_path().split("/")[2] == "occupations":
        return JsonResponse({"vocabulary": {'job': 'služba', 'surprise': 'presenečenje', 'to study': 'učiti se',
                                            'sure': 'gotovo', 'to choose': 'izbrati', 'to sound': 'zveneti',
                                            'policeman': 'policist', 'policewoman': '', 'pilot': 'pilot, pilotka',
                                            'engineer': 'inženir, inženirka', 'doctor': 'zdravnik, zdravnica',
                                            'photographer': 'fotograf, fotografinja', 'postman': 'poštar',
                                            'postwoman': 'poštarka', 'bus driver': 'voznik, voznica avtobusa',
                                            'taxi driver': 'taksist, taksistka', 'waiter': 'natakar',
                                            'waitress': 'natakarica', 'plumber': 'vodovodar, vodovodarka',
                                            'farmer': 'kmet, kmetica',
                                            'musician': 'glasbenik, glasbenica', 'cook': 'kuhar, kuharica',
                                            'businessman': 'poslovnež', 'businesswoman': 'poslovna ženska',
                                            'firefighter': 'gasilec, gasilka', 'teacher': 'učitelj, učiteljica',
                                            'lawyer': 'odvetnik, odvetnica', 'judge': 'sodnik, sodnica',
                                            'writer': 'pisatelj, pisateljica', 'poet': 'pesnik',
                                            'poetess': 'pesnica (občasno slabšalno)', 'actor': 'igralec',
                                            'actress': 'igralka',
                                            'builder': 'gradbenik, gradbenica', 'singer': 'pevec, pevka',
                                            'designer': 'oblikovalec, oblikovalka', 'priest': 'duhovnik',
                                            'librarian': 'knjižničar, knjižničarka', 'salesman': 'prodajalec',
                                            'saleswoman': 'prodajalka', 'to translate': 'prevesti',
                                            'to extinguish': 'pogasiti',
                                            'fire': 'ogenj', 'fashion': 'moda', 'industry': 'industrija',
                                            'result': 'rezultat', 'poetry': 'poezija', 'performance': 'nastop',
                                            'stage': 'oder',
                                            'cashier': 'blagajna', 'to build': 'graditi', 'house': 'hiša',
                                            'blackboard': '(šolska) tabla', 'cab': 'taksi',
                                            'to be surrounded': 'biti obkrožen',
                                            'guilty': 'kriv', 'whether': 'če, ali', 'to serve': 'streči',
                                            'to prepare': 'pripraviti', 'to bring': 'prinesti', 'mail': 'pošta',
                                            'to tell': 'povedati',
                                            'medicine': 'zdravilo', 'photograph': 'fotografija', 'plane': 'letalo',
                                            'gun': 'pištola', 'handcuffs': 'lisice'}})
