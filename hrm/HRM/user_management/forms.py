from django import forms
from .models import *

class RegisterForm(forms.Form):

    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    role = forms.CharField()
    personal_email = forms.EmailField()
    gender = forms.CharField()
    image = forms.ImageField()
    temporary_address = forms.CharField()
    permanent_address = forms.CharField()
    phone_number = forms.IntegerField()
    alternate_phone_number = forms.IntegerField()
    department = forms.CharField()
    joined_date = forms.DateField()
    password = forms.CharField()
    confirm_password = forms.CharField()

