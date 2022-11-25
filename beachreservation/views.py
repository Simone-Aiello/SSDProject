from django.shortcuts import render
from rest_framework import generics, permissions

from beachreservation.models import UmbrellaReservation
from beachreservation.serializers import RestrictedUmbrellaReservationSerializer


# Create your views here.
class UmbrellaReservationsList(generics.ListCreateAPIView):
    queryset = UmbrellaReservation.objects.all()
    serializer_class = RestrictedUmbrellaReservationSerializer
    # If I'm authenticated I can make POST request (only with my account), if not I can only see current reservations
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Calls the save method of serializer "imposing" the user who make the request to be the customer
    # NB this is done after the validation, this means that i cannot exclude customer from the serializer
    # Is this really the correct way?
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
