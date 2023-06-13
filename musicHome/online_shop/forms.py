from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput())
    email = forms.CharField(label='Эл. почта', widget=forms.TextInput())
    password1 = forms.CharField(label='Придумайте пароль', widget=forms.TextInput())
    password2 = forms.CharField(label='Повторите пароль', widget=forms.TextInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
