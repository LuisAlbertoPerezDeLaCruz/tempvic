from django import forms
from web.models import *

from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name','last_name')