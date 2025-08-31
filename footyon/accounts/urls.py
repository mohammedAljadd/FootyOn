from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from . import views

urlpatterns = [
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("signup/", views.signup, name="signup"),

]