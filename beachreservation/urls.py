from django.urls import path
from rest_framework.routers import SimpleRouter

from beachreservation.views import UmbrellaReservationsListCreateViewSet, UmbrellaReservationsRetrieveDeleteViewSet

router = SimpleRouter()

router.register('', UmbrellaReservationsListCreateViewSet, basename='reservations')
router.register('reservation-details', UmbrellaReservationsRetrieveDeleteViewSet, basename='user-reservations')
urlpatterns = router.urls
