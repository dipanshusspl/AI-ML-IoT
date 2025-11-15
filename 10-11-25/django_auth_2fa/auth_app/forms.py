from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class TOTPVerifyForm(forms.Form):
    token = forms.CharField(
        max_length=6, 
        min_length=6,
        label="6-Digit Code",
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'placeholder': '000000',
            'autocomplete': 'off'
        })
    )


class BackupCodeForm(forms.Form):
    backup_code = forms.CharField(
        label="Backup Code",
        max_length=8,
        widget=forms.TextInput(attrs={
            'placeholder': '12345678'
        })
    )