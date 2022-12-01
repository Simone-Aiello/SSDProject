from rest_framework.routers import SimpleRouter

from beachreservation.views import UmbrellaReservationsListCreateDestroyViewSet

router = SimpleRouter()

router.register('', UmbrellaReservationsListCreateDestroyViewSet, basename='reservations')
urlpatterns = router.urls
