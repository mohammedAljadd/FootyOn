# accounts/forms.py
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        # enforce "name + 3 digits"
        if not re.match(r"^[A-Za-z]+[0-9]{3}$", username):
            raise forms.ValidationError(
                "Username must be letters followed by exactly 3 digits (e.g. alex123)."
            )
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        # ensure only regular users are created
        user.is_staff = False
        user.is_superuser = False
        user.is_recruiter = False
        user.is_disabled = False
        if commit:
            user.save()
        return user
