from ucbenik.models import User
from django.contrib.auth.backends import BaseBackend

class CustomAuth(object):
    def authenticate(self, request, username=None, password=None):
        print("AUTH")
        user = User.objects.get(email=username)
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            print(user)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
