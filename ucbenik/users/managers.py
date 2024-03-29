from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail

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
        
        send_mail(
            'Dobrodošli v AKK',
            f'Pozdravljeni,\nuspešno ste ustvarili vaš račun za akk.si.\nemail: {email}\ngeslo: {password}',
            'info.akk.si@gmail.com',
            [email],
            fail_silently=False,
        )

        return user

    def create_superuser(self, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password, 'admin', 42, 'M')
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user