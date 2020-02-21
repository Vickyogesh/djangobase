from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone, six
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model
    """
    # username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=200)
    last_name = models.CharField(_('last name'), max_length=200)
    company_name = models.CharField(_('company name'), max_length=200)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'company_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)

    def get_short_name(self):
        return self.email

    def __str__(self):
        return "%s" % self.email


class registration(models.Model):
    username        = models.CharField(db_column='user', max_length=128)
    merchant_email  = models.CharField(db_column='email', max_length=128)
    password1       = models.CharField(max_length=128)
    firstname       = models.CharField(max_length=200)
    lastname        = models.CharField(max_length=200)
    companyname     = models.CharField(max_length=200)

    class Meta:
        db_table='app_registration'


class notification(models.Model):
    dateadded           = models.DateTimeField(blank=True, null=True)
    notificationvalue   = models.CharField(max_length=1000, blank=True, null=True)
    auth_user_id        = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table='app_notification'

