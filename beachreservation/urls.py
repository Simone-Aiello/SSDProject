from django.urls import path
from rest_framework.routers import SimpleRouter

from beachreservation.views import UmbrellaReservationsListCreateViewSet, UmbrellaReservationsListRetrieveDeleteViewSet

router = SimpleRouter()

router.register('', UmbrellaReservationsListCreateViewSet, basename='reservations')
router.register('reservation-details', UmbrellaReservationsListRetrieveDeleteViewSet, basename='user-reservations')
urlpatterns = router.urls
