from django.urls import path

from beachreservation.views import UmbrellaReservationsList

urlpatterns = [
    path('', UmbrellaReservationsList.as_view())
]