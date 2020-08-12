from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Solution, CharacterDataWomen, CharacterDataMen

admin.site.register(User, UserAdmin)
class SolutionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Solution, SolutionAdmin)

class MaleAvatarAdmin(admin.ModelAdmin):
    pass
admin.site.register(CharacterDataMen, MaleAvatarAdmin)

class FemaleAvatarAdmin(admin.ModelAdmin):
    pass
admin.site.register(CharacterDataWomen, FemaleAvatarAdmin)