from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

import razorpay
import hmac
import hashlib
import json
from decimal import Decimal

from .forms import RegisterForm
from .models import Booking, Wallet, WalletTransaction


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
    transactions = WalletTransaction.objects.filter(user=request.user)[:5]
    payment_configured = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
    return render(request, "accounts/dashboard.html", {
        "wallet": wallet,
        "bookings": bookings,
        "transactions": transactions,
        "payment_configured": payment_configured,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    })


@login_required
@require_POST
def wallet_payment_order(request):
    if not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET):
        return JsonResponse({"error": "Razorpay keys are not configured."}, status=503)

    try:
        amount = int(request.POST.get("amount", "0"))
        if not 1 <= amount <= 50000:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"error": "Enter an amount between ₹1 and ₹50,000."}, status=400)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "receipt": f"wallet-{request.user.id}-{WalletTransaction.objects.count() + 1}",
    })
    WalletTransaction.objects.create(
        user=request.user,
        amount=amount,
        provider_order_id=order["id"],
    )
    return JsonResponse({"order_id": order["id"], "amount": amount * 100})


@login_required
@require_POST
def verify_wallet_payment(request):
    try:
        payload = json.loads(request.body)
        order_id = payload["razorpay_order_id"]
        payment_id = payload["razorpay_payment_id"]
        signature = payload["razorpay_signature"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid payment response."}, status=400)

    signed_text = f"{order_id}|{payment_id}"
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        signed_text.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        return JsonResponse({"error": "Payment verification failed."}, status=400)

    with transaction.atomic():
        payment = WalletTransaction.objects.select_for_update().select_related("user__wallet").get(
            provider_order_id=order_id,
            user=request.user,
        )
        if payment.status != WalletTransaction.Status.CREATED:
            return JsonResponse({"success": True})
        payment.provider_payment_id = payment_id
        payment.status = WalletTransaction.Status.COMPLETED
        payment.save()
        wallet = Wallet.objects.select_for_update().get(user=request.user)
        wallet.balance += Decimal(payment.amount)
        wallet.save(update_fields=["balance"])
    return JsonResponse({"success": True, "balance": str(wallet.balance)})


@login_required
@require_POST
def demo_wallet_payment(request):
    if settings.RAZORPAY_KEY_ID or settings.RAZORPAY_KEY_SECRET:
        return JsonResponse({"error": "Demo mode is disabled when Razorpay keys are configured."}, status=400)
    try:
        amount = int(request.POST.get("amount", "0"))
        if not 1 <= amount <= 50000:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"error": "Enter an amount between ₹1 and ₹50,000."}, status=400)

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(user=request.user)
        wallet.balance += Decimal(amount)
        wallet.save(update_fields=["balance"])
        WalletTransaction.objects.create(
            user=request.user,
            amount=amount,
            provider="razorpay-demo",
            provider_order_id=f"demo_order_{request.user.id}_{WalletTransaction.objects.count() + 1}",
            provider_payment_id=f"demo_payment_{request.user.id}",
            status=WalletTransaction.Status.COMPLETED,
        )
    return JsonResponse({"success": True, "balance": str(wallet.balance)})
