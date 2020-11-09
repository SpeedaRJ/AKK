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
                          "Daily Routines": "lesson_two/daily_rountine/page_one"},
           "lesson_three": {"Pronouns": "/lesson_three/pronouns/page_one"}
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
    return render(request, "coming_soon.html", {"next": "/", "back": back,
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
        return render(request, "lesson2/time/page_nine.html", {"next": "/lesson_two/time/page_nine",
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
    back = "/lesson_two/present_simple/page_seventeen"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
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
                                                                        "back": back, "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Daily Routines",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def daily_routines_page_two(request):
    back = "/lesson_two/daily_routines/page_one"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
            return redirect(request.session['last_page'])
        request.session['last_page'] = request.path
        if 'avatar' in request.session:
            src_ref = request.session['avatar']['src_ref']
            parts = request.session['avatar']['parts']
            colors = request.session['avatar']['colors']
        else:
            src_ref, parts, colors = get_user_avatar(request.session['user'])
            request.session['avatar'] = {'src_ref': src_ref, 'parts': parts, 'colors': colors}
        return render(request, "lesson2/daily_routines/page_two.html", {"next": "/lesson_two/daily_routines/page_three",
                                                                        "back": back, "lessons": lessons,
                                                                        "lesson": "Unit 2", "title": "Daily Routines",
                                                                        "user": request.session['user'],
                                                                        "src": src_ref, "parts": parts, "colors": colors
                                                                        })


def daily_routines_page_three(request):
    back = "/lesson_two/daily_routines/page_two"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
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
                      {"next": "/lesson_two/daily_routines/page_three",
                       "back": back, "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def daily_routines_page_four(request):
    back = "/lesson_two/daily_routines/page_three"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
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
        return render(request, "lesson2/daily_routines/page_four.html",
                      {"next": "/lesson_two/daily_routines/page_five",
                       "back": back, "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
                       })


def daily_routines_page_five(request):
    back = "/lesson_two/daily_routines/page_four"
    if request.method == "GET":
        if 'user' not in request.session:
            return login_page(request)
        user = User.objects.get(email=request.session['user']['email'])
        if not get_refferer(request) and not user.is_staff:
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
        return render(request, "lesson2/daily_routines/page_five.html",
                      {"next": "/lesson_two/daily_routines/page_five",
                       "back": back, "lessons": lessons, "solved": solution.solved,
                       "lesson": "Unit 2", "title": "Daily Routines", "user": request.session['user'],
                       "src": src_ref, "parts": parts, "colors": colors
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
        return render(request, "lesson3/pronouns/page_seven.html", {"next": "/lesson_three/pronouns/page_seven",
                                                                    "back": "/lesson_three/pronouns/page_six",
                                                                    "solved": solution.solved,
                                                                    "lessons": lessons,
                                                                    "lesson": "Unit 3: Let's Eat", "title": "Pronouns",
                                                                    "user": request.session['user'],
                                                                    "src": src_ref, "parts": parts, "colors": colors
                                                                    })


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
