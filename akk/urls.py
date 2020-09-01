"""akk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ucbenik import views

urlpatterns = [
    #path('', views.home, name="home"),
    path('', views.index, name="home"),
    path('admin/', admin.site.urls),
    path("register", views.register, name="register"),
    path("login", views.login_page, name="login"),
    path("logout", views.logout, name="logout"),
    path("coming_soon", views.coming_soon, name="coming_soon"),
    path("update_session/<str:what_to_update>", views.update_session, name="update_session"),
    path("save_session", views.save_session, name="save_session"),
    path("lesson_one/title", views.lesson_one_title, name="title_one"),
    path("lesson_one/introduction/page_one", views.introduction_page_one, name="introduction_page_one"),
    path("lesson_one/introduction/page_two", views.introduction_page_two, name="introduction_page_two"),
    path("lesson_one/introduction/page_three", views.introduction_page_three, name="introduction_page_three"),
    path("lesson_one/introduction/page_four", views.introduction_page_four, name="introduction_page_four"),
    path("lesson_one/introduction/page_five", views.introduction_page_five, name="introduction_page_five"),
    path("lesson_one/introduction/page_six", views.introduction_page_six, name="introduction_page_six"),
    path("lesson_one/introduction/page_seven", views.introduction_page_seven, name="introduction_page_seven"),
    path("lesson_one/exercises/page_one", views.exercises_page_one, name="exercises_page_one"),
    path("lesson_one/exercises/page_two", views.exercises_page_two, name="exercises_page_two"),
    path("lesson_one/exercises/page_three", views.exercises_page_three, name="exercises_page_three"),
    path("lesson_one/exercises/page_four", views.exercises_page_four, name="exercises_page_four"),
    path("lesson_one/exercises/page_five", views.exercises_page_five, name="exercises_page_five"),
    path("lesson_one/exercises/page_six", views.exercises_page_six, name="exercises_page_six"),
    path("lesson_one/exercises/page_seven", views.exercises_page_seven, name="exercises_page_seven"),
    path("lesson_one/character_select/page_one", views.character_select_page_one, name="character_select_page_one"),
    path("lesson_one/character_select/page_two", views.character_select_page_two, name="character_select_page_two"),
    path("lesson_one/character_select/page_three", views.character_select_page_three, name="character_select_page_three"),
    path("lesson_one/character_select/page_four", views.character_select_page_four, name="character_select_page_four"),
    path("lesson_one/character_select/page_five", views.character_select_page_five, name="character_select_page_five"),
    path("lesson_one/character_select/page_six", views.character_select_page_six, name="character_select_page_six"),
    path("lesson_one/numbers/page_one", views.numbers_page_one, name="numbers_page_one"),
    path("lesson_one/numbers/page_two", views.numbers_page_two, name="numbers_page_two"),
    path("lesson_one/numbers/page_three", views.numbers_page_three, name="numbers_page_three"),
    path("lesson_one/numbers/page_four", views.numbers_page_four, name="numbers_page_four"),
    path("lesson_one/numbers/page_five", views.numbers_page_five, name="numbers_page_five"),
    path("lesson_one/numbers/page_six", views.numbers_page_six, name="numbers_page_six"),
    path("lesson_one/numbers/page_seven", views.numbers_page_seven, name="numbers_page_seven"),
    path("lesson_one/numbers/page_eight", views.numbers_page_eight, name="numbers_page_eight"),
    path("lesson_one/numbers/page_nine", views.numbers_page_nine, name="numbers_page_nine"),
    path("lesson_one/numbers/page_ten", views.numbers_page_ten, name="numbers_page_ten"),
    path("lesson_one/numbers/page_eleven", views.numbers_page_eleven, name="numbers_page_eleven"),
    path("lesson_one/numbers/page_twelve", views.numbers_page_twelve, name="numbers_page_twelve"),
    path("lesson_one/numbers/page_thirteen", views.numbers_page_thirteen, name="numbers_page_thirteen"),
    path("lesson_one/numbers/page_fourteen", views.numbers_page_fourteen, name="numbers_page_fourteen"),
    path("lesson_one/numbers/page_fifteen", views.numbers_page_fifteen, name="numbers_page_fifteen"),
    path("lesson_one/numbers/page_sixteen", views.numbers_page_sixteen, name="numbers_page_sixteen"),
    path("lesson_one/numbers/page_seventeen", views.numbers_page_seventeen, name="numbers_page_seventeen"),
    path("lesson_one/numbers/page_eighteen", views.numbers_page_eighteen, name="numbers_page_eighteen"),
    path("lesson_one/numbers/page_nineteen", views.numbers_page_nineteen, name="numbers_page_nineteen"),
    path("lesson_one/numbers/page_twenty", views.numbers_page_twenty, name="numbers_page_twenty"),
    path("lesson_one/numbers/page_twentyone", views.numbers_page_twentyone, name="numbers_page_twentyone"),
    path("lesson_one/numbers/page_twentytwo", views.numbers_page_twentytwo, name="numbers_page_twentytwo"),
    path("lesson_one/numbers/page_twentythree", views.numbers_page_twentythree, name="numbers_page_twentythree"),
    path("lesson_one/numbers/page_twentyfour", views.numbers_page_twentyfour, name="numbers_page_twentyfour"),
    path("lesson_one/numbers/page_twentyfive", views.numbers_page_twentyfive, name="numbers_page_twentyfive"),
    path("lesson_one/colors/page_one", views.colors_page_one, name="colors_page_one"),
    path("lesson_one/colors/page_two", views.colors_page_two, name="colors_page_two"),
    path("lesson_one/colors/page_three", views.colors_page_three, name="colors_page_three"),
    path("lesson_one/colors/page_four", views.colors_page_four, name="colors_page_four"),
    path("lesson_one/colors/page_five", views.colors_page_five, name="colors_page_five"),
    path("lesson_one/colors/page_six", views.colors_page_six, name="colors_page_six"),
    path("lesson_one/colors/page_seven", views.colors_page_seven, name="colors_page_seven"),
    path("lesson_one/colors/page_eight", views.colors_page_eight, name="colors_page_eight"),
    path("lesson_one/colors/page_nine", views.colors_page_nine, name="colors_page_nine"),
    path("lesson_one/years/page_one", views.years_page_one, name="years_page_one"),
    path("lesson_one/years/page_two", views.years_page_two, name="years_page_two"),
    path("lesson_one/years/page_three", views.years_page_three, name="years_page_three"),
    path("lesson_one/years/page_four", views.years_page_four, name="years_page_four"),
    path("lesson_one/years/page_five", views.years_page_five, name="years_page_five"),
    path("lesson_one/years/page_six", views.years_page_six, name="years_page_six"),
    path("lesson_one/years/page_seven", views.years_page_seven, name="years_page_seven"),
    path("lesson_one/years/page_eight", views.years_page_eight, name="years_page_eight"),
    path("lesson_one/years/page_nine", views.years_page_nine, name="years_page_nine"),
    path("lesson_one/years/page_ten", views.years_page_ten, name="years_page_ten"),
    path("lesson_one/years/page_eleven", views.years_page_eleven, name="years_page_eleven"),
    path("lesson_one/years/page_twelve", views.years_page_twelve, name="years_page_twelve"),
    path("lesson_one/personal_traits/page_one", views.personal_traits_page_one, name="personal_traits_page_one"),
    path("lesson_one/personal_traits/page_two", views.personal_traits_page_two, name="personal_traits_page_two"),
    path("lesson_one/personal_traits/page_three", views.personal_traits_page_three, name="personal_traits_page_three"),
    path("lesson_one/personal_traits/page_four", views.personal_traits_page_four, name="personal_traits_page_four"),
    path("lesson_one/personal_traits/page_five", views.personal_traits_page_five, name="personal_traits_page_five"),
    path("lesson_one/personal_traits/page_six", views.personal_traits_page_six, name="personal_traits_page_six"),
    path("lesson_one/personal_traits/page_seven", views.personal_traits_page_seven, name="personal_traits_page_seven"),
    path("lesson_one/he_she_it/page_one", views.he_she_it_page_one, name="he_she_it_page_one"),
    path("lesson_one/he_she_it/page_two", views.he_she_it_page_two, name="he_she_it_page_two"),
    path("lesson_one/he_she_it/page_three", views.he_she_it_page_three, name="he_she_it_page_three"),
    path("lesson_one/he_she_it/page_four", views.he_she_it_page_four, name="he_she_it_page_four"),
    path("lesson_one/he_she_it/page_five", views.he_she_it_page_five, name="he_she_it_page_five"),
    path("lesson_one/he_she_it/page_six", views.he_she_it_page_six, name="he_she_it_page_six"),
    path("lesson_one/he_she_it/page_seven", views.he_she_it_page_seven, name="he_she_it_page_seven"),
    path("lesson_one/he_she_it/page_eight", views.he_she_it_page_eight, name="he_she_it_page_eight"),
    path("lesson_one/he_she_it/page_nine", views.he_she_it_page_nine, name="he_she_it_page_nine"),
    path("lesson_one/he_she_it/page_ten", views.he_she_it_page_ten, name="he_she_it_page_ten"),
    path("lesson_one/he_she_it/page_eleven", views.he_she_it_page_eleven, name="he_she_it_page_eleven"),
    path("lesson_one/he_she_it/page_twelve", views.he_she_it_page_twelve, name="he_she_it_page_twelve"),
    path("lesson_one/he_she_it/page_thirteen", views.he_she_it_page_thirteen, name="he_she_it_page_thirteen"),
    path("lesson_one/he_she_it/page_fourteen", views.he_she_it_page_fourteen, name="he_she_it_page_fourteen"),
    path("lesson_one/he_she_it/page_fifteen", views.he_she_it_page_fifteen, name="he_she_it_page_fifteen"),
    path("lesson_one/he_she_it/page_sixteen", views.he_she_it_page_sixteen, name="he_she_it_page_sixteen"),
    path("lesson_one/he_she_it/page_seventeen", views.he_she_it_page_seventeen, name="he_she_it_page_seventeen"),
    path("lesson_one/he_she_it/page_eighteen", views.he_she_it_page_eighteen, name="he_she_it_page_eighteen"),
    path("lesson_one/he_she_it/page_nineteen", views.he_she_it_page_nineteen, name="he_she_it_page_nineteen"),
    path("lesson_one/he_she_it/page_twenty", views.he_she_it_page_twenty, name="he_she_it_page_twenty"),
    path("lesson_one/he_she_it/page_twentyone", views.he_she_it_page_twentyone, name="he_she_it_page_twentyone"),
    path("lesson_one/he_she_it/page_twentytwo", views.he_she_it_page_twentytwo, name="he_she_it_page_twentytwo"),
    path("lesson_one/he_she_it/page_twentythree", views.he_she_it_page_twentythree, name="he_she_it_page_twentythree"),
    path("lesson_one/he_she_it/page_twentyfour", views.he_she_it_page_twentyfour, name="he_she_it_page_twentyfour"),
    path("lesson_one/he_she_it/page_twentyfive", views.he_she_it_page_twentyfive, name="he_she_it_page_twentyfive"),
    path("lesson_one/he_she_it/page_twentysix", views.he_she_it_page_twentysix, name="he_she_it_page_twentysix"),
    path("lesson_one/he_she_it/page_twentyseven", views.he_she_it_page_twentyseven, name="he_she_it_page_twentyseven"),
    path("lesson_one/he_she_it/page_twentyeight", views.he_she_it_page_twentyeight, name="he_she_it_page_twentyeight"),
    path("lesson_one/he_she_it/page_twentynine", views.he_she_it_page_twentynine, name="he_she_it_page_twentynine"),
    path("lesson_one/he_she_it/page_thirty", views.he_she_it_page_thirty, name="he_she_it_page_thirty"),
    path("lesson_one/he_she_it/page_thirtyone", views.he_she_it_page_thirtyone, name="he_she_it_page_thirtyone"),
    path("lesson_one/he_she_it/page_thirtytwo", views.he_she_it_page_thirtytwo, name="he_she_it_page_thirtytwo"),
    path("lesson_one/he_she_it/page_thirtythree", views.he_she_it_page_thirtythree, name="he_she_it_page_thirtythree"),
    path("lesson_one/he_she_it/page_thirtyfour", views.he_she_it_page_thirtyfour, name="he_she_it_page_thirtyfour"),
    path("lesson_one/he_she_it/page_thirtyfive", views.he_she_it_page_thirtyfive, name="he_she_it_page_thirtyfive"),
    path("lesson_one/he_she_it/page_thirtysix", views.he_she_it_page_thirtysix, name="he_she_it_page_thirtysix"),
    path("lesson_one/he_she_it/page_thirtyseven", views.he_she_it_page_thirtyseven, name="he_she_it_page_thirtyseven"),
    path("lesson_one/he_she_it/page_thirtyeight", views.he_she_it_page_thirtyeight, name="he_she_it_page_thirtyeight"),
    path("lesson_one/he_she_it/page_thirtynine", views.he_she_it_page_thirtynine, name="he_she_it_page_thirtynine"),
    path("lesson_one/he_she_it/page_forty", views.he_she_it_page_forty, name="he_she_it_page_forty"),
    path("lesson_one/he_she_it/page_fortyone", views.he_she_it_page_fortyone, name="he_she_it_page_fortyone"),
    path("lesson_one/he_she_it/page_fortytwo", views.he_she_it_page_fortytwo, name="he_she_it_page_fortytwo"),
#Lesson2
    path("lesson_two/title", views.lesson_two_title, name="title_two"),   
    path("lesson_two/day_week_month/page_one", views.day_week_month_page_one, name="day_week_month_page_one"),   
    path("lesson_two/day_week_month/page_two", views.day_week_month_page_two, name="day_week_month_page_two"),   
    path("lesson_two/day_week_month/page_three", views.day_week_month_page_three, name="day_week_month_page_three"),   
    path("lesson_two/day_week_month/page_four", views.day_week_month_page_four, name="day_week_month_page_four"),   
    path("lesson_two/day_week_month/page_five", views.day_week_month_page_five, name="day_week_month_page_five"),   
    path("lesson_two/day_week_month/page_six", views.day_week_month_page_six, name="day_week_month_page_six"),   
    path("lesson_two/day_week_month/page_seven", views.day_week_month_page_seven, name="day_week_month_page_seven"),   
    path("lesson_two/day_week_month/page_eight", views.day_week_month_page_eight, name="day_week_month_page_eight"),   
    path("lesson_two/day_week_month/page_nine", views.day_week_month_page_nine, name="day_week_month_page_nine"),   
    path("lesson_two/day_week_month/page_ten", views.day_week_month_page_ten, name="day_week_month_page_ten"),
    path("lesson_two/day_week_month/page_eleven", views.day_week_month_page_eleven, name="day_week_month_page_eleven"),
    path("lesson_two/day_week_month/page_twelve", views.day_week_month_page_twelve, name="day_week_month_page_twelve"),
    path("lesson_two/articles/page_one", views.articles_page_one, name="articles_page_one"),   
    path("lesson_two/articles/page_two", views.articles_page_two, name="articles_page_two"),      
#Lesson3
    path("lesson_three/title", views.lesson_three_title, name="title_three"),
    path("lesson_three/pronouns/page_one", views.pronouns_page_one, name="pronouns_page_one"),
    path("lesson_three/pronouns/page_two", views.pronouns_page_two, name="pronouns_page_two"),
    path("lesson_three/pronouns/page_three", views.pronouns_page_three, name="pronouns_page_three"),
    path("lesson_three/pronouns/page_four", views.pronouns_page_four, name="pronouns_page_four"),
    path("lesson_three/pronouns/page_five", views.pronouns_page_five, name="pronouns_page_five"),
    path("lesson_three/pronouns/page_six", views.pronouns_page_six, name="pronouns_page_six"),
]
