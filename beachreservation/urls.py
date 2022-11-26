from django.urls import path
from rest_framework.routers import SimpleRouter

from beachreservation.views import UmbrellaReservationsListCreateViewSet

router = SimpleRouter()

router.register('', UmbrellaReservationsListCreateViewSet, basename='reservations')
urlpatterns = router.urls
