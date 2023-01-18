from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "login_form-input", "placeholder": "Логин"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "login_form-input", "placeholder": "Пароль"}))
