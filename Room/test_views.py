from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import Max
from .models import Room, Booking


class RoomViewTestCase(TestCase):

    def setUp(self):

        Room1 = Room.objects.create(room_code=1,room_name="cn330",room_capacity=10,available_hours=2,is_available = True)
        Room2 = Room.objects.create(room_code=2,room_name="cn33",room_capacity=20,available_hours=1,is_available = False)

    def test_home_view_home(self):
           c = Client()
           response = c.get(reverse('Room:home'))
           self.assertEqual(response.status_code, 200)
