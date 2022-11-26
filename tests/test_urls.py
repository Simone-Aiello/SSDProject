import datetime
import json

import pytest
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.test import APIClient

from beachreservation import utils


@pytest.fixture
def reservations(db):
    return [
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=datetime.date.today(), reservation_end_date=datetime.date.today()),
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=2,
                    reservation_start_date=datetime.date.today(),
                    reservation_end_date=datetime.date.today() + relativedelta(days=1)),
        mixer.blend('beachreservation.UmbrellaReservation', number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=3,
                    reservation_start_date=datetime.date.today(),
                    reservation_end_date=datetime.date.today() + relativedelta(days=3))
    ]


def get_client(user=None):
    res = APIClient()
    if user is not None:
        res.force_login(user)
    return res


def parse(response):
    response.render()
    content = response.content.decode()
    return json.loads(content)


def test_anon_user_cant_make_post_requests():
    path = reverse('reservations-list')
    client = get_client()
    response = client.post(path)
    assert response.status_code == HTTP_403_FORBIDDEN


def test_anon_user_can_make_get_requests(reservations):
    path = reverse('reservations-list')
    client = get_client()
    response = client.get(path)
    assert response.status_code == HTTP_200_OK
    obj = parse(response)
    assert len(obj) == len(reservations)


def test_logged_user_can_make_get_requests(reservations):
    path = reverse('reservations-list')
    client = get_client(mixer.blend(get_user_model()))
    response = client.get(path)
    assert response.status_code == HTTP_200_OK
    obj = parse(response)
    assert len(obj) == len(reservations)


def test_logged_user_can_make_post_requests(reservations):
    path = reverse('reservations-list')
    user = mixer.blend(get_user_model())
    client = get_client(user)
    reservation = {'customer': user.id, 'number_of_seats': 2, 'reservation_start_date': datetime.date.today(), 'reservation_end_date': datetime.date.today(), 'reserved_umbrella_id': 10}
    response = client.post(path, reservation)
    assert response.status_code == HTTP_201_CREATED


def test_logged_user_cant_make_posts_request_for_other_users(reservations):
    path = reverse('reservations-list')
    victim_user = mixer.blend(get_user_model())
    logged_user = mixer.blend(get_user_model())
    client = get_client(logged_user)
    reservation = {'customer': victim_user.id, 'number_of_seats': 3, 'reservation_start_date': datetime.date.today(),
                   'reservation_end_date': datetime.date.today(), 'reserved_umbrella_id': 10}
    response = client.post(path, reservation)
    assert response.status_code == HTTP_403_FORBIDDEN

