from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, firstname, age, sex, is_staff=False):
        """
        Create and save a User with the given email and password.
        """
        if is_staff:
            return self.create_superuser(email, password)
        if not email:
            raise ValueError(_('The Email must be set'))

        email = self.normalize_email(email)
        user = self.model(username=email,email=email, first_name=firstname, age=age, sex=sex)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password, 'admin', 42, 'M')
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user