from datetime import time
from django.test import TestCase

from .models import Train


class TrainTests(TestCase):
    def setUp(self):
        self.train = Train.objects.create(
            train_no="12345", train_name="RailEase Express",
            source="Delhi", destination="Mumbai",
            departure_time=time(8, 0), arrival_time=time(20, 0),
            fare=999, total_seats=100, available_seats=100,
        )

    def test_train_status_page(self):
        response = self.client.get("/train-status/", {"train_no": "12345"})
        self.assertEqual(response.status_code, 200)

    def test_train_list_page(self):
        response = self.client.get("/trains/")
        self.assertContains(response, "RailEase Express")
