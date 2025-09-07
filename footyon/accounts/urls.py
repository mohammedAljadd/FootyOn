from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from . import views

urlpatterns = [
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("signup/", views.signup, name="signup"),
    path("manage/", views.manage_accounts, name="manage_accounts"),
    path("toggle/<int:user_id>/", views.toggle_account_status, name="toggle_account_status"),
]