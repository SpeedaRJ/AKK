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
    path("lesson_one/character_select/page_two", views.character_select_page_two, name="character_select_page_two"),
    path("lesson_one/character_select/page_two", views.character_select_page_two, name="character_select_page_two"),
    path("lesson_one/character_select/page_two", views.character_select_page_two, name="character_select_page_two"),
    path("lesson_one/character_select/page_two", views.character_select_page_two, name="character_select_page_two"),
]
