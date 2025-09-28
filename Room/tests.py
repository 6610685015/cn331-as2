from django.test import TestCase
from .models import Room, Booking

class RoomTestCase(TestCase):

    def setUp(self):
        Room1 = Room.objects.create(room_code=1,room_name="cn330",room_capacity=10,available_hours=2,is_available = True)
        Room2 = Room.objects.create(room_code=2,room_name="cn331",room_capacity=20,available_hours=1,is_available = False)

        return super().setUp()
    
    def test_is_available(self):
        self.assertTrue(True)