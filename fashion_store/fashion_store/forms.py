from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from django import forms

class ResetPasswordForm(PasswordResetForm):
    email = forms.EmailField(label='Email', help_text='Please input your Email', min_length=2, max_length=100, widget=forms.EmailInput(
        attrs={'class': 'input-round big-input', 'placeholder': 'name@email.com', 'id': 'email'}
    ))

class ChangePasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New Password', strip=False, help_text='Please input secure Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'input-round big-input', 'placeholder': '* * * * * * * * * *'}
    ))
    new_password2 = forms.CharField(label='New Password Confirmation', strip=False, help_text='Please input secure Password', min_length=8, max_length=100, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'input-round big-input', 'placeholder': '* * * * * * * * * *'}
    ))