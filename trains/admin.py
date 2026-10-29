from django.contrib import admin

from .models import Train


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("train_no", "train_name", "source", "destination", "available_seats")
    search_fields = ("train_no", "train_name", "source", "destination")
