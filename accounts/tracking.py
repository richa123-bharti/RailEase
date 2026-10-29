from django.db import models

class TrainStatus(models.Model):

    train_no = models.CharField(
        max_length=10
    )

    current_station = models.CharField(
        max_length=100
    )

    previous_station = models.CharField(
        max_length=100
    )

    next_station = models.CharField(
        max_length=100
    )

    delay_minutes = models.IntegerField(
        default=0
    )

    eta = models.CharField(
        max_length=50
    )

    def __str__(self):
        return self.train_no