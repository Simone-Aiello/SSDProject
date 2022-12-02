import datetime

from django.db.models import Q
from rest_framework import permissions, status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from beachreservation import utils
from beachreservation.models import UmbrellaReservation
from beachreservation.serializers import RestrictedUmbrellaReservationSerializer, FullUmbrellaReservationSerializer


class CreateListDestroyViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class UmbrellaReservationsListCreateDestroyViewSet(CreateListDestroyViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RestrictedUmbrellaReservationSerializer
        else:
            return FullUmbrellaReservationSerializer

    def get_queryset(self):
        # If we are querying this endpoint as a beach manager you can see all the reservations
        if self.request.user.groups.filter(name='beach-managers').exists():
            return UmbrellaReservation.objects.all()

        # If we are logged in but not as a beach manager then you receive only our reservations
        else:
            return UmbrellaReservation.objects.all().filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class FreeUmbrellaInADateRange(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start_date_initial = request.GET.get('start_date', None)
        end_date_initial = request.GET.get('end_date', None)
        if start_date_initial is None or end_date_initial is None:
            return Response(data={"res": "Start date and End date parameters are required"},
                            status=HTTP_400_BAD_REQUEST)
        try:
            start_date = datetime.datetime.strptime(start_date_initial, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_initial, '%Y-%m-%d').date()
        except ValueError:
            return Response(data={"res": "Date format must be yyyy-mm-dd"}, status=HTTP_400_BAD_REQUEST)

        if end_date < start_date:
            return Response(data={"res": "End date can't be after start date"}, status=HTTP_400_BAD_REQUEST)

        criterion1 = Q(reservation_start_date__lte=end_date)
        criterion2 = Q(reservation_end_date__gte=start_date)

        overlapping_reservations_umbrella_id = UmbrellaReservation.objects.filter(criterion1 & criterion2).values_list(
            'reserved_umbrella_id', flat=True)

        free_umbrella_id = [i for i in range(utils.MIN_UMBRELLA_ID, utils.MAX_UMBRELLA_ID + 1) if
                            i not in overlapping_reservations_umbrella_id]

        return Response(data={"res": free_umbrella_id}, status=HTTP_200_OK)
