from django.shortcuts import render, redirect
from .forms import UserSignupForm

def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = UserSignupForm()
    return render(request, "accounts/signup.html", {"form": form})
