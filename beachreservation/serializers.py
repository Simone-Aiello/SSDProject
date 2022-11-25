import datetime

from rest_framework import serializers

from beachreservation.models import UmbrellaReservation


class RestrictedUmbrellaReservationSerializer(serializers.ModelSerializer):
    class Meta:
        # TODO: How to remove the customer from here? if I exclude it I can't use this serializers for POST request
        # because it says 'this field cannot be null' even if i override the perform_create in the view because
        # the validation is called before and it causes problems
        fields = ('id', 'customer', 'number_of_seats', 'reservation_start_date', 'reservation_end_date', 'reserved_umbrella_id')
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
        try:
            instance.full_clean()
            return attrs
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.args[0])
