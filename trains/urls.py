from django.urls import path

from .views import book_train, cancel_booking, home, pnr_status, ticket, train_list, train_status

urlpatterns = [
    path("", home, name="home"),
    path("trains/", train_list, name="train_list"),
    path("trains/<int:train_id>/book/", book_train, name="book_train"),
    path("train-status/", train_status, name="train_status"),
    path("pnr-status/", pnr_status, name="pnr_status"),
    path("ticket/<str:pnr>/", ticket, name="ticket"),
    path("booking/<str:pnr>/cancel/", cancel_booking, name="cancel_booking"),
]
