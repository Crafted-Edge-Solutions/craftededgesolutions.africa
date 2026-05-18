from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages


@login_required
def home(request):
    sub = getattr(request.user, "insights_subscription", None)
    return render(request, "dashboard/home.html", {"sub": sub})


@login_required
def billing(request):
    sub = getattr(request.user, "insights_subscription", None)
    return render(request, "dashboard/billing.html", {"sub": sub})


@login_required
def profile(request):
    user = request.user
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])
        messages.success(request, "Profile updated.")
        return redirect("dashboard:profile")
    return render(request, "dashboard/profile.html", {})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password updated successfully.")
        return redirect("dashboard:profile")
    return render(request, "dashboard/change_password.html", {"form": form})
