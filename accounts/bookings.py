from django.db import models
from django.contrib.auth.models import User
from trains.models import Train
import random

class Booking(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE
    )

    passenger_name = models.CharField(
        max_length=100
    )

    seat_no = models.IntegerField()

    pnr = models.CharField(
        max_length=10,
        unique=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default="Confirmed"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["train", "seat_no"],
                condition=models.Q(status="Confirmed"),
                name="unique_confirmed_seat_per_train",
            )
        ]

    def save(self, *args, **kwargs):
        if not self.pnr:
            while True:
                pnr = str(random.randint(1000000000, 9999999999))
                if not Booking.objects.filter(pnr=pnr).exists():
                    self.pnr = pnr
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.pnr