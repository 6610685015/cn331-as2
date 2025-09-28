from django.test import TestCase
from django.contrib.auth.models import User
from .models import Room, Booking

# ----------------------------
# Test ห้องและ Booking ทั่วไป
# ----------------------------
class RoomTestCase(TestCase):
    def setUp(self):
        # สร้าง user
        self.user = User.objects.create_user(username="testuser", password="12345")

        # สร้างห้องตัวอย่าง
        self.room1 = Room.objects.create(
            room_code=101,
            room_name="Conference",
            room_capacity=10,
            available_hours=2,
            is_available=True,
        )
        self.room2 = Room.objects.create(
            room_code=102,
            room_name="Meeting",
            room_capacity=20,
            available_hours=0,
            is_available=False,
        )

        # สร้าง booking สำหรับ room1
        self.booking1 = Booking.objects.create(
            room=self.room1,
            username=self.user.username
        )

    def test_room_created(self):
        self.assertEqual(Room.objects.count(), 2)
        self.assertEqual(self.room1.room_name, "Conference")
        self.assertEqual(self.room2.room_capacity, 20)

    def test_is_available_flag(self):
        self.assertTrue(self.room1.is_available)
        self.assertFalse(self.room2.is_available)

    def test_available_hours(self):
        self.room1.available_hours -= 1
        self.room1.save()
        self.room1.refresh_from_db()
        self.assertEqual(self.room1.available_hours, 1)

    def test_room_str(self):
        self.assertEqual(str(self.room1), "Conference (101)")

    def test_booking_str(self):
        self.assertEqual(str(self.booking1), f"testuser ({self.room1.room_code})")

# ----------------------------
# Test การจอง
# ----------------------------
class BookingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

        self.room = Room.objects.create(
            room_code=101,
            room_name="Conference",
            room_capacity=10,
            available_hours=2,
            is_available=True,
        )
        self.room_unavailable = Room.objects.create(
            room_code=102,
            room_name="Meeting",
            room_capacity=5,
            available_hours=0,
            is_available=False,
        )

    def test_booking_creation(self):
        booking = Booking.objects.create(room=self.room, username=self.user.username)
        # ลด available_hours หลังจอง
        self.room.available_hours -= 1
        self.room.save()

        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.room, self.room)
        self.assertEqual(booking.username, self.user.username)
        self.room.refresh_from_db()
        self.assertEqual(self.room.available_hours, 1)

    def test_booking_unavailable_room(self):
        # ไม่ควรสร้าง booking เมื่อ room ไม่ว่างหรือ available_hours=0
        if self.room_unavailable.is_available and self.room_unavailable.available_hours > 0:
            Booking.objects.create(room=self.room_unavailable, username=self.user.username)
        self.assertEqual(Booking.objects.filter(room=self.room_unavailable).count(), 0)

    def test_booking_duplicate(self):
        Booking.objects.create(room=self.room, username=self.user.username)
        duplicate = Booking.objects.filter(room=self.room, username=self.user.username)
        self.assertTrue(duplicate.exists())

    def test_cancel_booking(self):
        booking = Booking.objects.create(room=self.room, username=self.user.username)
        # ยกเลิก booking
        room_id = booking.room_id
        booking.delete()
        room = Room.objects.get(pk=room_id)
        room.available_hours += 1
        room.save()
        room.refresh_from_db()
        self.assertEqual(room.available_hours, 3)

# ----------------------------
# Test แก้ไขและลบห้อง
# ----------------------------
class RoomEditDeleteTestCase(TestCase):
    def setUp(self):
        # สร้าง user สำหรับ booking
        self.user = User.objects.create_user(username="testuser", password="12345")

        # สร้าง rooms
        self.room1 = Room.objects.create(
            room_code=101,
            room_name="Conference",
            room_capacity=10,
            available_hours=24,
            is_available=True,
        )
        self.room2 = Room.objects.create(
            room_code=102,
            room_name="Meeting",
            room_capacity=20,
            available_hours=12,
            is_available=True,
        )

        # สร้าง booking สำหรับ room1
        self.booking1 = Booking.objects.create(room=self.room1, username=self.user.username)

    def test_edit_room(self):
        # แก้ไข room1
        self.room1.room_code = 103
        self.room1.room_name = "Training"
        self.room1.room_capacity = 15
        self.room1.available_hours = 10
        self.room1.is_available = False
        self.room1.save()

        updated = Room.objects.get(pk=self.room1.pk)
        self.assertEqual(updated.room_code, 103)
        self.assertEqual(updated.room_name, "Training")
        self.assertEqual(updated.room_capacity, 15)
        self.assertEqual(updated.available_hours, 10)
        self.assertFalse(updated.is_available)

    def test_edit_room_duplicate_code(self):
        duplicate_exists = Room.objects.filter(room_code=self.room2.room_code).exclude(pk=self.room1.pk).exists()
        self.assertTrue(duplicate_exists)

    def test_delete_room(self):
        room_id = self.room1.id
        self.room1.delete()
        self.assertFalse(Room.objects.filter(id=room_id).exists())
