from django.shortcuts import render, redirect
from .forms import UserSignupForm
from django.contrib.auth.decorators import user_passes_test
from .models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = UserSignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def manage_accounts(request):
    users = User.objects.all().order_by("username")
    return render(request, "accounts/manage_accounts.html", {"users": users})

@user_passes_test(is_admin)
def toggle_account_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Prevent superuser from disabling themselves
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("manage_accounts")

    user.is_disabled = not user.is_disabled
    user.save()

    if user.is_disabled:
        messages.warning(request, _("🚫 %(username)s has been deactivated.") % {'username': user.username})
    else:
        messages.success(request, _("✅ %(username)s has been activated.") % {'username': user.username})

    return redirect("manage_accounts")