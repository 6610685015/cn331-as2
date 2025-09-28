from django.urls import path
from django.contrib import admin
from . import views
app_name="Room"
urlpatterns = [
    path("home/", views.home, name="home"),
    path("available-room/", views.allroom, name="available"),
    path("selectroom/<int:room_code>/", views.selectroom1, name="selectroom"),
    path("see-booking/", views.mybooking, name="mybooking"),
    path("addroom/", views.addroom, name="addroom"),
    path("saveroom/", views.saveroom, name="saveroom"),
    path("booking/", views.booking, name="booking"),
    path("cancel/", views.cancel, name="cancel"),
    path("delete-room-page/", views.deletepage, name="deletepage"),
    path("deleteroom/", views.deleteroom, name="deleteroom"),
    path("editroom/<int:room_code>/", views.editroom, name="editroom"),
    path("see-all-booking", views.allbooking, name="allbooking"),
]
