from django.urls import path
from rest_framework.routers import SimpleRouter

from beachreservation.views import UmbrellaReservationsListCreateDestroyViewSet, FreeUmbrellaInADateRange

router = SimpleRouter()

router.register('', UmbrellaReservationsListCreateDestroyViewSet, basename='reservations')
urlpatterns = router.urls
urlpatterns.append(path('freeumbrella', FreeUmbrellaInADateRange.as_view()))
