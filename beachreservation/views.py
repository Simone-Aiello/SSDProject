from rest_framework import permissions, status, mixins, viewsets
from rest_framework.response import Response

from beachreservation.models import UmbrellaReservation
from beachreservation.serializers import RestrictedUmbrellaReservationSerializer, FullUmbrellaReservationSerializer


class CreateListDestroyViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class UmbrellaReservationsListCreateDestroyViewSet(CreateListDestroyViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RestrictedUmbrellaReservationSerializer
        else:
            return FullUmbrellaReservationSerializer

    def get_queryset(self):
        # If we are querying this endpoint as a beach manager we retrieve all the reservations
        if self.request.user.groups.filter(name='beach-managers').exists():
            return UmbrellaReservation.objects.all()

        # If we are logged in but not as a beach manager then we receive only our requests
        else:
            return UmbrellaReservation.objects.all().filter(customer=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.data['customer'] != f"{request.user.id}":
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
