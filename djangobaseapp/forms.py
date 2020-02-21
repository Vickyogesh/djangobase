from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core import signing
from django import forms
from datetime import timedelta
from djangobaseapp import models
import requests


class Tool_ASIN(forms.Form):
    asin = forms.CharField()


class RegisterUser(UserCreationForm):
    email = forms.CharField(max_length=128)
    password1 = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    company_name = forms.CharField(max_length=200)

    class Meta:
        model = models.User
        fields = (
            'first_name',
            'last_name',
            'company_name',
            'email',
            'password1'
        )


class RegistrationForm(UserCreationForm):
    merchant_email  = forms.CharField(max_length=100)
    password1       = forms.CharField(widget=forms.PasswordInput())
    firstname       = forms.CharField(max_length=200)
    lastname        = forms.CharField(max_length=200)
    companyname     = forms.CharField(max_length=200)

    class Meta:
        model = models.User
        fields = ('firstname','lastname','companyname','email', 'password1')

    def clean_email(self):
        #verify email is valid and does not exist already in the table.
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def clean_password2(self):
        '''
        Password Validation
        '''

        #verify passwords match
        password1   = self.cleaned_data['password1']
        password2   = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError("passwords do not match")

    def clean_accountid(self):
        #verify valid account id and passphrase
        accountid = self.cleaned_data['AccountID']
        table = models.transactiontable()
        return accountid

    def save(self, commit=True):
        #save the user
        user = super(RegistrationForm, self).save(commit=False)
        if commit:
            if 1 ==2:
                pass
            else:
                return {
                    "status":400,
                    "message":"Invalid credentials"
                }

    def confirm_login_allowed(self, user):
        if not user.is_active or not user.is_validated:
            raise forms.ValidationError('There was a problem with your login.', code='invalid_login')
