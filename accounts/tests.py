from django.contrib.auth.models import User
from django.test import TestCase

from .wallet import Wallet


class WalletTests(TestCase):
    def test_wallet_created_for_new_user(self):
        user = User.objects.create_user("traveller", password="testpass123")
        self.assertTrue(Wallet.objects.filter(user=user).exists())
