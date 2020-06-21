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
    path("lesson_one/introduction/page_one", views.introduction_page_one, name="introduction_page_one"),
    path("lesson_one/introduction/page_two", views.introduction_page_two, name="introduction_page_two"),
    path("lesson_one/introduction/page_three", views.introduction_page_three, name="introduction_page_three"),
    path("lesson_one/introduction/page_four", views.introduction_page_four, name="introduction_page_four"),
    path("lesson_one/introduction/page_five", views.introduction_page_five, name="introduction_page_five"),
    path("lesson_one/introduction/page_six", views.introduction_page_six, name="introduction_page_six")
]
