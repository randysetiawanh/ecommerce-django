from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import *
from django import forms

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(label='Username', help_text='Please input your Username', min_length=4, max_length=20, widget=forms.TextInput(
        attrs={'class': 'input-round big-input', 'placeholder': 'Input Username', 'id': 'username'}
    ))
    password = forms.CharField(label='Password', help_text='Please input secure Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'input-round big-input', 'placeholder': 'Input Password', 'id': 'password'}
    ))

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label='First Name', help_text='Please input your first name', min_length=2, max_length=50, widget=forms.TextInput(
        attrs={'class': 'input-round big-input', 'placeholder': 'Input First Name', 'id': 'first_name'}
    ))
    last_name = forms.CharField(label='Last Name', help_text='Please input your last name', min_length=2, max_length=50, widget=forms.TextInput(
        attrs={'class': 'input-round big-input', 'placeholder': 'Input Last Name', 'id': 'last_name'}
    ))
    username = UsernameField(label='Username', help_text='Please input your Username', min_length=4, max_length=20, widget=forms.TextInput(
        attrs={'class': 'input-round big-input', 'placeholder': 'Input Username', 'id': 'username'}
    ))
    email = forms.EmailField(label='Email', help_text='Please input your Email', min_length=2, max_length=100, widget=forms.EmailInput(
        attrs={'class': 'input-round big-input', 'placeholder': 'name@email.com', 'id': 'email'}
    ))
    password1 = forms.CharField(label='Password', strip=False, help_text='Please input secure Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'input-round big-input', 'placeholder': '* * * * * * * * * *'}
    ))
    password2 = forms.CharField( label='Password Confirmation', strip=False, help_text='Please input again Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'input-round big-input', 'placeholder': '* * * * * * * * * *'}
    ))

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already register! Please try again.")
        elif User.objects.filter(email=email).exists():
            raise ValidationError("Email already register! Please try again.")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2',)

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', help_text='Please input secure Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'input-round big-input', 'placeholder': '* * * * * * * * * *', 'id': 'old_password'}
    ))
    new_password1 = forms.CharField(label='New Password', strip=False, help_text='Please input secure Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'input-round big-input', 'placeholder': '* * * * * * * * * *'}
    ))
    new_password2 = forms.CharField(label='New Password Confirmation', strip=False, help_text='Please input secure Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'input-round big-input', 'placeholder': '* * * * * * * * * *'}
    ))

class ContactForm(forms.Form):
    nameContact = forms.CharField(max_length = 100, widget = forms.TextInput(
        attrs={'placeholder': 'Your Name', 'id': 'nameContact'}
    ))
    emailContact = forms.EmailField(max_length = 150, widget = forms.EmailInput(
        attrs={'placeholder': 'Your Email', 'id': 'emailContact'}
    ))
    messageContact = forms.CharField(max_length = 2000, widget = forms.Textarea(
        attrs={'placeholder': 'Your Message', 'id': 'messageContact'}
    ))

class APWNForm(forms.Form):
    nameProduct = forms.CharField(label='Product Name', max_length = 100, widget = forms.TextInput(
        attrs={'placeholder': 'Product Name', 'class' : 'input-round big-input', 'id': 'nameProduct'}
    ))
    priceProduct = forms.FloatField(label='Product Price', widget = forms.NumberInput(
        attrs={'placeholder': 'Price Product', 'class' : 'input-round big-input', 'id': 'priceProduct'}
    ))
    imageProduct = forms.ImageField(label='Product Image', widget = forms.FileInput(
        attrs={'class' : 'input-round big-input', 'id': 'imageProduct'}
    ))
    categoryProduct = forms.ModelChoiceField(label='Product Category', queryset=Category.objects.all(), widget = forms.Select(
        attrs={'class' : 'input-round big-input'}
    ))
    descriptionProduct = forms.CharField(label='Product Description', widget=forms.Textarea(
        attrs={'class' : 'input-round big-input', 'rows':3, 'cols':5}
    ))
