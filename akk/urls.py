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
    path('', views.home, name="home"),
    path('admin/', admin.site.urls),
    path("register", views.register, name="register"),
    path("login", views.login_page, name="login"),
    path("update_session/<str:what_to_update>", views.update_session, name="update_session"),
    path("lesson_one/introduction/page_one", views.introduction_page_one, name="introduction_page_one"),
    path("lesson_one/introduction/page_two", views.introduction_page_two, name="introduction_page_two"),
    path("lesson_one/introduction/page_three", views.introduction_page_three, name="introduction_page_three"),
    path("lesson_one/introduction/page_four", views.introduction_page_four, name="introduction_page_four"),
    path("lesson_one/introduction/page_five", views.introduction_page_five, name="introduction_page_five"),
    path("lesson_one/introduction/page_six", views.introduction_page_six, name="introduction_page_six"),
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
    path("lesson_one/colors/page_one", views.colors_page_one, name="colors_page_one"),
    path("lesson_one/colors/page_two", views.colors_page_two, name="colors_page_two"),
    path("lesson_one/colors/page_three", views.colors_page_three, name="colors_page_three"),
    path("lesson_one/colors/page_four", views.colors_page_four, name="colors_page_four"),
    path("lesson_one/colors/page_five", views.colors_page_five, name="colors_page_five"),
    path("lesson_one/colors/page_six", views.colors_page_six, name="colors_page_six"),
    path("lesson_one/colors/page_seven", views.colors_page_seven, name="colors_page_seven"),
    path("lesson_one/colors/page_eight", views.colors_page_eight, name="colors_page_eight"),
    path("lesson_one/colors/page_nine", views.colors_page_nine, name="colors_page_nine"),
]
