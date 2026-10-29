from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Booking, TrainStatus, Wallet
from .models import Train


def home(request):
    return render(request, "trains/home.html")


def train_status(request):
    train_no = request.GET.get("train_no", "").strip()
    status = TrainStatus.objects.filter(train_no__iexact=train_no).first() if train_no else None
    return render(request, "trains/status.html", {
        "train_no": train_no,
        "status": status,
        "searched": bool(train_no),
    })


@require_http_methods(["GET"])
def pnr_status(request):
    pnr = request.GET.get("pnr", "").strip()
    booking = Booking.objects.select_related("train", "user").filter(pnr=pnr).first() if pnr else None
    return render(request, "trains/pnr_status.html", {
        "pnr": pnr,
        "booking": booking,
        "searched": bool(pnr),
    })


def train_list(request):
    trains = Train.objects.all()
    source = request.GET.get("source", "")
    destination = request.GET.get("destination", "")
    aliases = {
        'madhya pradesh': 'bhopal',
        'mp': 'bhopal',
        'bihar': 'patna',
        'new delhi': 'delhi',
    }
    if source:
        source_key = aliases.get(source.strip().lower(), source)
        trains = trains.filter(source__icontains=source_key)
    if destination:
        destination_key = aliases.get(destination.strip().lower(), destination)
        trains = trains.filter(destination__icontains=destination_key)
    trains = trains.filter(available_seats__gt=0).order_by("departure_time")
    return render(request, "trains/train_list.html", {"trains": trains, "source": source, "destination": destination})


@login_required
@transaction.atomic
def book_train(request, train_id):
    train = get_object_or_404(Train.objects.select_for_update(), pk=train_id)
    wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)

    if request.method == "POST":
        passenger_name = request.POST.get("passenger_name", "").strip()
        seat_no = request.POST.get("seat_no", "")
        if not passenger_name:
            messages.error(request, "Passenger name is required.")
        elif train.available_seats < 1:
            messages.error(request, "No seats are available on this train.")
        elif wallet.balance < train.fare:
            messages.error(request, "Insufficient wallet balance.")
        else:
            try:
                seat_no = int(seat_no)
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid seat number.")
            else:
                if seat_no < 1 or seat_no > train.total_seats:
                    messages.error(request, "Seat number is outside the train capacity.")
                elif Booking.objects.filter(train=train, seat_no=seat_no, status="Confirmed").exists():
                    messages.error(request, "That seat is already booked. Please choose another seat.")
                else:
                    try:
                        with transaction.atomic():
                            Booking.objects.create(user=request.user, train=train, passenger_name=passenger_name, seat_no=seat_no)
                            Train.objects.filter(pk=train.pk).update(available_seats=F("available_seats") - 1)
                            wallet.balance -= train.fare
                            wallet.save(update_fields=["balance"])
                    except IntegrityError:
                        messages.error(request, "That seat was just booked. Please choose another seat.")
                    else:
                        messages.success(request, "Booking confirmed.")
                        return redirect("dashboard")

    return render(request, "trains/book.html", {"train": train})


@login_required
@transaction.atomic
def cancel_booking(request, pnr):
    booking = get_object_or_404(Booking.objects.select_for_update().select_related("train"), pnr=pnr, user=request.user)
    if request.method == "POST" and booking.status != "Cancelled":
        booking.status = "Cancelled"
        booking.save(update_fields=["status"])
        Train.objects.filter(pk=booking.train_id).update(available_seats=F("available_seats") + 1)
        wallet = Wallet.objects.select_for_update().get(user=request.user)
        wallet.balance += booking.train.fare
        wallet.save(update_fields=["balance"])
        messages.success(request, f"Booking {pnr} cancelled and fare refunded.")
        return redirect("dashboard")
    return redirect("dashboard")


@login_required
def ticket(request, pnr):
    booking = get_object_or_404(Booking.objects.select_related("train", "user"), pnr=pnr, user=request.user)
    return render(request, "trains/ticket.html", {"booking": booking})
