from django.db import models

class Train(models.Model):

    train_no = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)

    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    fare = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    total_seats = models.IntegerField()
    available_seats = models.IntegerField()

    def __str__(self):
        return self.train_name
