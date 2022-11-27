import datetime
import json

import pytest
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
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


class TestUmbrellaReservationsListCreateViewSet:
    def test_anon_user_cant_make_post_requests(self):
        path = reverse('reservations-list')
        client = get_client()
        response = client.post(path)
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_anon_user_can_make_get_requests(self, reservations):
        path = reverse('reservations-list')
        client = get_client()
        response = client.get(path)
        assert response.status_code == HTTP_200_OK
        obj = parse(response)
        assert len(obj) == len(reservations)

    def test_logged_user_can_make_get_requests(self, reservations):
        path = reverse('reservations-list')
        client = get_client(mixer.blend(get_user_model()))
        response = client.get(path)
        assert response.status_code == HTTP_200_OK
        obj = parse(response)
        assert len(obj) == len(reservations)

    def test_logged_user_can_make_post_requests(self, reservations):
        path = reverse('reservations-list')
        user = mixer.blend(get_user_model())
        client = get_client(user)
        reservation = {'customer': user.id, 'number_of_seats': 2, 'reservation_start_date': datetime.date.today(),
                       'reservation_end_date': datetime.date.today(), 'reserved_umbrella_id': 10}
        response = client.post(path, reservation)
        assert response.status_code == HTTP_201_CREATED

    def test_logged_user_cant_make_posts_request_for_other_users(self, reservations):
        path = reverse('reservations-list')
        victim_user = mixer.blend(get_user_model())
        logged_user = mixer.blend(get_user_model())
        client = get_client(logged_user)
        reservation = {'customer': victim_user.id, 'number_of_seats': 3,
                       'reservation_start_date': datetime.date.today(),
                       'reservation_end_date': datetime.date.today(), 'reserved_umbrella_id': 10}
        response = client.post(path, reservation)
        assert response.status_code == HTTP_403_FORBIDDEN


class TestUmbrellaReservationsRetrieveDeleteViewSet:
    tested_endpoint = 'user-reservations'

    def test_anon_user_cant_make_requests_to_detail_endpoint(self, reservations):
        path = reverse(f"{self.tested_endpoint}-detail", kwargs={'pk': reservations[0].pk})
        client = get_client()
        get_request_response = client.get(path)
        delete_request_response = client.delete(path)
        assert get_request_response.status_code == HTTP_403_FORBIDDEN
        assert delete_request_response.status_code == HTTP_403_FORBIDDEN

    def test_anon_user_cant_make_requests_to_list_endpoint(self, reservations):
        path = reverse(f"{self.tested_endpoint}-list")
        client = get_client()
        get_request_response = client.get(path)
        assert get_request_response.status_code == HTTP_403_FORBIDDEN

    def test_logged_user_cant_see_not_owned_reservations(self, reservations):
        not_owned_reservation_path = reverse(f"{self.tested_endpoint}-detail", kwargs={'pk': reservations[0].pk})
        user = mixer.blend(get_user_model())
        client = get_client(user)
        get_response = client.get(not_owned_reservation_path)
        delete_response = client.delete(not_owned_reservation_path)
        assert get_response.status_code == HTTP_404_NOT_FOUND
        assert delete_response.status_code == HTTP_404_NOT_FOUND

    def test_logged_user_can_see_and_delete_owned_reservations(self, db):
        user = mixer.blend(get_user_model())
        reservation = mixer.blend('beachreservation.UmbrellaReservation', customer=user,
                                  number_of_seats=utils.MIN_SEAT_UMBRELLA,
                                  reserved_umbrella_id=1,
                                  reservation_start_date=datetime.date.today(),
                                  reservation_end_date=datetime.date.today())
        path = reverse(f"{self.tested_endpoint}-detail", kwargs={'pk': reservation.pk})
        client = get_client(user)
        get_response = client.get(path)
        delete_response = client.delete(path)
        assert get_response.status_code == HTTP_200_OK
        assert delete_response.status_code == HTTP_204_NO_CONTENT

    def test_logged_user_can_only_retrieve_his_own_reservation(self, db):
        user1 = mixer.blend(get_user_model())
        user2 = mixer.blend(get_user_model())
        path = reverse(f"{self.tested_endpoint}-list")
        mixer.blend('beachreservation.UmbrellaReservation', customer=user1, number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=1,
                    reservation_start_date=datetime.date.today(), reservation_end_date=datetime.date.today()),
        mixer.blend('beachreservation.UmbrellaReservation', customer=user1, number_of_seats=utils.MIN_SEAT_UMBRELLA,
                    reserved_umbrella_id=2,
                    reservation_start_date=datetime.date.today(),
                    reservation_end_date=datetime.date.today() + relativedelta(days=1)),
        mixer.blend('beachreservation.UmbrellaReservation', customer=user2, number_of_seats=utils.MAX_SEAT_UMBRELLA,
                    reserved_umbrella_id=3,
                    reservation_start_date=datetime.date.today(),
                    reservation_end_date=datetime.date.today() + relativedelta(days=3))
        client = get_client(user1)
        response = client.get(path)
        obj = parse(response)
        result_customer_list = [o['customer'] for o in obj]
        assert response.status_code == HTTP_200_OK
        assert len(obj) == 2
        assert all([idx == user1.id for idx in result_customer_list])
