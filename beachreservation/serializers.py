import datetime

from rest_framework import serializers

from beachreservation.models import UmbrellaReservation


def check_if_data_is_after_or_equal_today(data):
    if data < datetime.date.today():
        raise serializers.ValidationError("Reservation date can't be in the past")


def check_if_model_is_full_clean(model):
    try:
        model.full_clean()
    except serializers.ValidationError as e:
        raise serializers.ValidationError(e.args[0])


class FullUmbrellaReservationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'customer', 'number_of_seats', 'reservation_start_date', 'reservation_end_date',
            'reserved_umbrella_id', 'reservation_price')
        model = UmbrellaReservation

    # TODO: ask professor if this is usefull for internal database corruption
    def validate_reservation_start_date(self, data):
        check_if_data_is_after_or_equal_today(data)
        return data

    def validate_reservation_end_date(self, data):
        check_if_data_is_after_or_equal_today(data)
        return data

    def validate(self, attrs):
        instance = UmbrellaReservation(**attrs)
        check_if_model_is_full_clean(instance)
        return attrs


class RestrictedUmbrellaReservationSerializer(serializers.ModelSerializer):
    class Meta:
        # TODO: How to remove the customer from here? if I exclude it I can't use this serializers for POST request
        # because it says 'this field cannot be null' even if i override the perform_create in the view because
        # the validation is called before and it causes problems
        fields = (
            'id', 'customer', 'number_of_seats', 'reservation_start_date', 'reservation_end_date',
            'reserved_umbrella_id')
        model = UmbrellaReservation

    # TODO: ask professor how can we test this (do we need to test it?)
    def validate_reservation_start_date(self, data):
        if data < datetime.date.today():
            raise serializers.ValidationError("Start date can't be in the past")
        return data

    def validate_reservation_end_date(self, data):
        if data < datetime.date.today():
            raise serializers.ValidationError("End date can't be in the past")
        return data

    def validate(self, attrs):
        instance = UmbrellaReservation(**attrs)
        check_if_model_is_full_clean(instance)
        return attrs
