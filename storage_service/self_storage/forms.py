from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailInput, TextInput, PasswordInput


User = get_user_model()

class RegisterUser(UserCreationForm):
    password1 = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
            'placeholder': 'Пароль'
            }),
    )
    password2 = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']
        widgets = {
            'email': EmailInput(attrs={
                'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                'placeholder': 'E-mail'
                }),
            'username': TextInput(attrs={
                'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                'placeholder': 'Имя пользователя'
                }),
        }
