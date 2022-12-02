import datetime

import pytest
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
from dateutil.relativedelta import relativedelta
from beachreservation import utils


def test_cant_book_for_overlapped_reservations(db):
    reservation_start_date = datetime.date(2022, 12, 20)
    reservation_end_date = datetime.date(2022, 12, 25)
    mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                reserved_umbrella_id=1,
                reservation_start_date=reservation_start_date, reservation_end_date=reservation_end_date)
    invalid_reservations = [
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=datetime.date(2022, 12, 19),
                    reservation_end_date=datetime.date(2022, 12, 22)),
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=datetime.date(2022, 12, 19),
                    reservation_end_date=datetime.date(2022, 12, 28)),
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=datetime.date(2022, 12, 21),
                    reservation_end_date=datetime.date(2022, 12, 22)),
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=datetime.date(2022, 12, 20),
                    reservation_end_date=datetime.date(2022, 12, 26)),
    ]
    for invalid_data in invalid_reservations:
        with pytest.raises(ValidationError):
            invalid_data.full_clean()


def test_str_method_umbrella_reservation(db):
    res = mixer.blend('beachreservation.UmbrellaReservation')
    assert str(res) == f"{res.id}: {res.customer} from {res.reservation_start_date} to {res.reservation_end_date}"


def test_price_calculation_in_umbrella_reservation(db):
    today_date = datetime.date.today()
    valid_reservations = [
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=today_date, reservation_end_date=today_date),
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=today_date, reservation_end_date=today_date + relativedelta(days=1)),
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=today_date, reservation_end_date=today_date + relativedelta(days=3))
    ]
    corresponding_correct_price = [40, 60, 180]
    for idx, res in enumerate(valid_reservations):
        assert res.reservation_price == corresponding_correct_price[idx]


def test_invalid_reservation_values(db):
    today_date = datetime.date.today()
    invalid_reservations = [

        # Number of seats below minimum

        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA - 1,
                    reserved_umbrella_id=1,
                    reservation_start_date=today_date, reservation_end_date=today_date),
        # Number of seats above maximum
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA + 1,
                    reserved_umbrella_id=2,
                    reservation_start_date=today_date, reservation_end_date=today_date),

        # End date before start date
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=5,
                    reservation_start_date=today_date + relativedelta(days=1), reservation_end_date=today_date),

        # Reserved umbrella id above the maximum
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=utils.MAX_UMBRELLA_ID + 1,
                    reservation_start_date=today_date, reservation_end_date=today_date),
        # Reserved umbrella id below the minimum
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=utils.MIN_UMBRELLA_ID - 1,
                    reservation_start_date=today_date, reservation_end_date=today_date),
    ]
    for reservation in invalid_reservations:
        with pytest.raises(ValidationError) as e:
            reservation.full_clean()


def test_valid_model_values(db):
    today_date = datetime.date.today()
    valid_values = [
        # Number of seats equals to the minimum
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=2, reservation_start_date=today_date, reservation_end_date=today_date),

        # Number of seats equals to the maximum
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=3, reservation_start_date=today_date, reservation_end_date=today_date),

        # Reserved umbrella id equals to the minimum
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=utils.MIN_UMBRELLA_ID, reservation_start_date=today_date,
                    reservation_end_date=today_date),

        # Reserved umbrella id equals to the maximum
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=utils.MAX_UMBRELLA_ID, reservation_start_date=today_date,
                    reservation_end_date=today_date),

        # A < B with dates overlapping
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=utils.MAX_UMBRELLA_ID, reservation_start_date=today_date - relativedelta(days=2),
                    reservation_end_date=today_date - relativedelta(days=1)),

        # A > B with dates overlapping
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=utils.MAX_UMBRELLA_ID,
                    reservation_start_date=today_date + relativedelta(days=1),
                    reservation_end_date=today_date + relativedelta(days=2)),
    ]
    for value in valid_values:
        value.full_clean()
