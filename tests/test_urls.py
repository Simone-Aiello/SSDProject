import datetime
import json

import pytest
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, \
    HTTP_204_NO_CONTENT
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


class TestUmbrellaReservationsListCreateDestroyViewSet:
    def test_anon_user_cant_make_post_requests(self):
        path = reverse('reservations-list')
        client = get_client()
        response = client.post(path)
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_anon_user_cant_make_get_requests(self, reservations):
        path = reverse('reservations-list')
        client = get_client()
        response = client.get(path)
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_anon_user_cant_make_delete_requests(self, reservations):
        path = reverse("reservations-detail", kwargs={'pk': reservations[0].pk})
        client = get_client()
        delete_request_response = client.delete(path)
        assert delete_request_response.status_code == HTTP_403_FORBIDDEN

    def test_logged_user_can_make_get_requests_and_receive_own_reservations(self, db):
        path = reverse('reservations-list')
        user = mixer.blend(get_user_model())
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
        mixer.blend('beachreservation.UmbrellaReservation', customer=user, number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=29,
                    reservation_start_date=datetime.date.today(),
                    reservation_end_date=datetime.date.today() + relativedelta(days=1))
        mixer.blend('beachreservation.UmbrellaReservation', customer=user, number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=30,
                    reservation_start_date=datetime.date.today(),
                    reservation_end_date=datetime.date.today() + relativedelta(days=1))
        client = get_client(user)
        response = client.get(path)
        parsed_res = parse(response)
        assert len(parsed_res) == 2
        assert all([user.id == res["customer"] for res in parsed_res])

    def test_customer_user_can_make_post_requests(self, reservations):
        path = reverse('reservations-list')
        user = mixer.blend(get_user_model())
        client = get_client(user)
        reservation = {'number_of_seats': 2, 'reservation_start_date': datetime.date.today(),
                       'reservation_end_date': datetime.date.today(), 'reserved_umbrella_id': 10}
        response = client.post(path, reservation)

        assert response.status_code == HTTP_201_CREATED

    def test_logged_user_can_delete_owned_reservations(self, db):
        user = mixer.blend(get_user_model())
        reservation = mixer.blend('beachreservation.UmbrellaReservation', customer=user,
                                  number_of_seats=utils.MIN_SEAT_UMBRELLA, reserved_umbrella_id=1,
                                  reservation_start_date=datetime.date.today(),
                                  reservation_end_date=datetime.date.today())
        path = reverse("reservations-detail", kwargs={'pk': reservation.pk})
        client = get_client(user)
        delete_response = client.delete(path)
        assert delete_response.status_code == HTTP_204_NO_CONTENT

    def test_customer_user_cant_delete_not_owned_reservations(self, reservations):
        path = reverse("reservations-detail", kwargs={'pk': reservations[0].pk})
        user = mixer.blend(get_user_model())
        client = get_client(user)
        response = client.delete(path)
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_beach_manager_can_make_get_requests_and_receive_all_reservations(self, reservations):
        path = reverse('reservations-list')
        user = mixer.blend(get_user_model())
        group = mixer.blend(Group, name='beach-managers')
        user.groups.add(group)
        client = get_client(user)
        response = client.get(path)
        assert response.status_code == HTTP_200_OK
        assert len(parse(response)) == len(reservations)

    def test_beach_manager_can_make_post_requests(self, db):
        path = reverse('reservations-list')
        user = mixer.blend(get_user_model())
        group = mixer.blend(Group, name='beach-managers')
        user.groups.add(group)
        client = get_client(user)
        reservation = {'customer': user.id, 'number_of_seats': 3, 'reservation_start_date': datetime.date.today(),
                       'reservation_end_date': datetime.date.today(), 'reserved_umbrella_id': 14}
        response = client.post(path, reservation)
        assert response.status_code == HTTP_201_CREATED

    def test_beach_manager_can_delete_user_reservations(self, reservations):
        path = reverse("reservations-detail", kwargs={'pk': reservations[0].pk})
        user = mixer.blend(get_user_model())
        group = mixer.blend(Group, name='beach-managers')
        user.groups.add(group)
        client = get_client(user)
        response = client.delete(path)
        assert response.status_code == HTTP_204_NO_CONTENT
