from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from . import views
from .forms import UserLoginForm  # Import our custom login form with placeholders

urlpatterns = [
    # Logout view - redirects to home page after logout
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
    # Login view - uses our custom UserLoginForm instead of Django's default
    # This ensures placeholders are used instead of labels
    path("login/", LoginView.as_view(
        template_name="accounts/login.html",  # Template to render
        authentication_form=UserLoginForm  # Our custom form with placeholders
    ), name="login"),
    
    # Signup view - handled by custom view function
    path("signup/", views.signup, name="signup"),
    
    # Admin view to manage all user accounts (requires superuser)
    path("manage/", views.manage_accounts, name="manage_accounts"),
    
    # Admin action to activate/deactivate a user account (requires superuser)
    # <int:user_id> captures the user's ID from the URL
    path("toggle/<int:user_id>/", views.toggle_account_status, name="toggle_account_status"),
]