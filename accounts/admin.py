from django.contrib import admin

from .models import Booking, TrainStatus, Wallet


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("pnr", "passenger_name", "train", "seat_no", "status", "user")
    search_fields = ("pnr", "passenger_name")


@admin.register(TrainStatus)
class TrainStatusAdmin(admin.ModelAdmin):
    list_display = ("train_no", "current_station", "next_station", "delay_minutes", "eta")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")
