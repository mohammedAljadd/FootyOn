# accounts/forms.py
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.utils.translation import gettext_lazy as _

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
        
    def __init__(self, *args, **kwargs):
        """
        Override __init__ to customize form fields with placeholders instead of labels.
        This prevents layout shifts when translated text becomes longer.
        """
        # Call parent class __init__ first to initialize the form
        super().__init__(*args, **kwargs)
        
        # ===== USERNAME FIELD =====
        # Update the username field widget attributes
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Username (e.g. alex123)'),  # Placeholder text (translatable)
            'class': 'form-control'  # Bootstrap class for styling
        })
        self.fields['username'].label = ''  # Remove label to avoid duplication
        
        # ===== PASSWORD1 FIELD (Password) =====
        # Update the first password field widget attributes
        self.fields['password1'].widget.attrs.update({
            'placeholder': _('Password'),  # Placeholder text (translatable)
            'class': 'form-control'  # Bootstrap class for styling
        })
        self.fields['password1'].label = ''  # Remove label
        # Keep the help text - it shows password requirements to users
        # Django's default help text explains: length, similarity, common passwords, numeric-only rules
        
        # ===== PASSWORD2 FIELD (Confirm Password) =====
        # Update the password confirmation field widget attributes
        self.fields['password2'].widget.attrs.update({
            'placeholder': _('Confirm Password'),  # Placeholder text (translatable)
            'class': 'form-control'  # Bootstrap class for styling
        })
        self.fields['password2'].label = ''  # Remove label
        
        # ===== REMOVE HELP TEXT =====
        # Django's default password fields include help text about password requirements
        # We remove them to keep the form clean and minimal
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['username'].help_text = ''

    def clean_username(self):
        """
        Custom validation for username field.
        Enforces format: letters followed by exactly 3 digits (e.g., alex123)
        """
        username = self.cleaned_data.get("username")
        # Regex pattern: ^[A-Za-z]+ = one or more letters, [0-9]{3}$ = exactly 3 digits
        if not re.match(r"^[A-Za-z]+[0-9]{3}$", username):
            raise forms.ValidationError(
                _("Username must be letters followed by exactly 3 digits (e.g. alex123).")
            )
        return username

    def save(self, commit=True):
        """
        Override save method to ensure security defaults.
        Prevents privilege escalation during signup.
        """
        # Create user object but don't save to database yet
        user = super().save(commit=False)
        
        # Ensure only regular users are created (not admins or staff)
        user.is_staff = False
        user.is_superuser = False
        user.is_recruiter = False
        user.is_disabled = False
        
        # Save to database if commit=True
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Custom login form that uses placeholders instead of labels.
    Extends Django's built-in AuthenticationForm.
    """
    def __init__(self, *args, **kwargs):
        """
        Customize the login form fields with placeholders.
        """
        # Call parent class __init__ to initialize the form
        super().__init__(*args, **kwargs)
        
        # ===== USERNAME FIELD =====
        # AuthenticationForm uses 'username' field by default
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Username'),  # Placeholder text (translatable)
            'class': 'form-control'  # Bootstrap class for styling
        })
        self.fields['username'].label = ''  # Remove label
        
        # ===== PASSWORD FIELD =====
        # AuthenticationForm uses 'password' field (not password1/password2)
        self.fields['password'].widget.attrs.update({
            'placeholder': _('Password'),  # Placeholder text (translatable)
            'class': 'form-control'  # Bootstrap class for styling
        })
        self.fields['password'].label = ''  # Remove label