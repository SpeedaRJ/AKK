from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Solution

admin.site.register(User, UserAdmin)
class SolutionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Solution, SolutionAdmin)