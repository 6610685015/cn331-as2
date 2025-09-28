from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Room, Booking

class RoomViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # สร้าง user และ login
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

        # สร้างห้องตัวอย่าง
        self.room1 = Room.objects.create(
            room_code=1,
            room_name="cn330",
            room_capacity=10,
            available_hours=2,
            is_available=True,
        )
        self.room2 = Room.objects.create(
            room_code=2,
            room_name="cn331",
            room_capacity=5,
            available_hours=0,
            is_available=False,
        )

    def test_home_view(self):
        response = self.client.get(reverse("Room:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/home.html")

    def test_allroom_view(self):
        response = self.client.get(reverse("Room:available"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.room_name)
        self.assertContains(response, self.room2.room_name)

    def test_selectroom_view(self):
        response = self.client.get(reverse("Room:selectroom", args=[self.room1.room_code]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.room_name)

    def test_addroom_view_get(self):
        response = self.client.get(reverse("Room:addroom"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/addroom.html")

    def test_saveroom_view_post(self):
        response = self.client.post(
            reverse("Room:saveroom"),
            {
                "room_code": 3,
                "room_name": "cn332",
                "room_capacity": 8,
                "available_hours": 4,
                "room_state": "True",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Room.objects.filter(room_code=3).exists())

    def test_saveroom_view_get_default_render(self):
        # Trigger line: return render(request, "room/addroom.html") สำหรับ GET
        response = self.client.get(reverse("Room:saveroom"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/addroom.html")

    def test_deletepage_view(self):
        response = self.client.get(reverse("Room:deletepage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/deleteroom.html")

    def test_deleteroom_view_post(self):
        response = self.client.post(reverse("Room:deleteroom"), {"room_code": self.room2.room_code}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Room.objects.filter(pk=self.room2.pk).exists())

    def test_editroom_view_get(self):
        response = self.client.get(reverse("Room:editroom", args=[self.room1.room_code]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/editroom.html")

    def test_editroom_view_post(self):
        response = self.client.post(
            reverse("Room:editroom", args=[self.room1.room_code]),
            {
                "room_code": 4,
                "room_name": "cn333",
                "room_capacity": 12,
                "available_hours": 3,
                "room_state": "False",
            },
            follow=True,
        )
        self.room1.refresh_from_db()
        self.assertEqual(self.room1.room_code, 4)
        self.assertEqual(self.room1.room_name, "cn333")
        self.assertEqual(self.room1.room_capacity, 12)
        self.assertFalse(self.room1.is_available)

    def test_editroom_duplicate_post(self):
        # Trigger condition: room_code already exists
        response = self.client.post(
            reverse("Room:editroom", args=[self.room1.room_code]),
            {
                "room_code": self.room2.room_code,
                "room_name": "duplicate",
                "room_capacity": 5,
                "available_hours": 2,
                "room_state": "True",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This room code already exist.")

    def test_mybooking_view(self):
        Booking.objects.create(room=self.room1, username=self.user.username)
        response = self.client.get(reverse("Room:mybooking"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.room_name)

    def test_booking_view_post(self):
        response = self.client.post(reverse("Room:booking"), {"room_code": self.room1.room_code}, follow=True)
        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.filter(room=self.room1, username=self.user.username).first()
        self.assertIsNotNone(booking)
        self.room1.refresh_from_db()
        self.assertEqual(self.room1.available_hours, 1)

    def test_booking_unavailable_room(self):
        response = self.client.post(reverse("Room:booking"), {"room_code": self.room2.room_code}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(room=self.room2, username=self.user.username).exists())

    def test_booking_get_default_render(self):
        # Trigger line: return render(request, "room/home.html") สำหรับ GET
        response = self.client.get(reverse("Room:booking"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/home.html")

    def test_cancel_view(self):
        booking = Booking.objects.create(room=self.room1, username=self.user.username)
        response = self.client.get(reverse("Room:cancel") + f"?id={booking.id}", follow=True)
        self.room1.refresh_from_db()
        self.assertEqual(self.room1.available_hours, 3)

    def test_allbooking_view_get(self):
        # สร้าง booking เพื่อให้ context['allbooking'] มีข้อมูล
        Booking.objects.create(room=self.room1, username=self.user.username)
        
        # เรียก view แบบ GET
        response = self.client.get(reverse("Room:allbooking"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/allbooking.html")
        
        # ตรวจ context ว่ามี booking
        self.assertIn('allbooking', response.context)
        self.assertEqual(len(response.context['allbooking']), 1)
        self.assertEqual(response.context['allbooking'][0].room, self.room1)
