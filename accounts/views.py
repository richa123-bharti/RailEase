from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .models import Booking, Wallet


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.save()
            Wallet.objects.get_or_create(user=user)
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    bookings = Booking.objects.filter(user=request.user).select_related("train").order_by("-id")
    return render(request, "accounts/dashboard.html", {"wallet": wallet, "bookings": bookings})
