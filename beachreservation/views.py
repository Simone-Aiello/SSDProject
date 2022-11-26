from rest_framework import permissions, status, mixins, viewsets
from rest_framework.response import Response

from beachreservation.models import UmbrellaReservation
from beachreservation.serializers import RestrictedUmbrellaReservationSerializer


class CreateListRetrieveViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class UmbrellaReservationsListCreateViewSet(CreateListRetrieveViewSet):
    queryset = UmbrellaReservation.objects.all()
    serializer_class = RestrictedUmbrellaReservationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        if request.data['customer'] != f"{request.user.id}":
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
