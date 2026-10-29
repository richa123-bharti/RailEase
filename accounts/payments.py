from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class WalletTransaction(models.Model):
    class Status(models.TextChoices):
        CREATED = "Created", "Created"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallet_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=30, default="razorpay")
    provider_order_id = models.CharField(max_length=100, blank=True)
    provider_payment_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} - {self.status}"
