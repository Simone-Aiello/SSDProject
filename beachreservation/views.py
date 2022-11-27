from rest_framework import permissions, status, mixins, viewsets
from rest_framework.response import Response

from beachreservation.models import UmbrellaReservation
from beachreservation.serializers import RestrictedUmbrellaReservationSerializer, FullUmbrellaReservationSerializer


class CreateListRetrieveViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class ListRetrieveDeleteViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


# TODO: Maybe we can remove the List View (?)
class UmbrellaReservationsListCreateViewSet(CreateListRetrieveViewSet):
    queryset = UmbrellaReservation.objects.all()
    serializer_class = RestrictedUmbrellaReservationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        if request.data['customer'] != f"{request.user.id}":
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class UmbrellaReservationsRetrieveDeleteViewSet(ListRetrieveDeleteViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FullUmbrellaReservationSerializer

    def get_queryset(self):
        return UmbrellaReservation.objects.filter(customer=self.request.user)
