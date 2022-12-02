import datetime

from django.core.exceptions import ValidationError
from rest_framework import serializers

from beachreservation.models import UmbrellaReservation


def check_if_data_is_after_or_equal_today(date):
    if date < datetime.date.today():
        raise serializers.ValidationError("Reservation date can't be in the past")


def check_if_model_is_clean(model):
    try:
        model.clean()
    except ValidationError as e:
        raise serializers.ValidationError(e.args[0])


class FullUmbrellaReservationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'customer', 'number_of_seats', 'reservation_start_date', 'reservation_end_date',
            'reserved_umbrella_id', 'reservation_price')
        model = UmbrellaReservation


class RestrictedUmbrellaReservationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'number_of_seats', 'reservation_start_date', 'reservation_end_date',
            'reserved_umbrella_id')
        model = UmbrellaReservation

    def validate_reservation_start_date(self, date):
        check_if_data_is_after_or_equal_today(date)
        return date

    def validate_reservation_end_date(self, date):
        check_if_data_is_after_or_equal_today(date)
        return date

    def validate(self, attrs):
        instance = UmbrellaReservation(**attrs)
        check_if_model_is_clean(instance)
        return attrs
