import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def create_customer(api_client):
    def do_create_customer(customer):
        return api_client.post('/store/customers/', customer)
    return do_create_customer


@pytest.fixture
def force_authenticate(api_client):
    def do_force_authenticate(is_staff=False):
        api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_force_authenticate


@pytest.mark.django_db
class TestCreateCustomer:
    def test_if_user_is_ananymous_returns_401(self, create_customer):
        response = create_customer({
            'first_name': 'Jhon',
            'last_name': 'Smith',
            'phone_number': '775555555',
            'is_consumer': False
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, create_customer, force_authenticate):
        force_authenticate()
        response = create_customer({
            'first_name': 'Jhon',
            'last_name': 'Smith',
            'phone_number': '775555555',
            'is_consumer': False
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, create_customer, force_authenticate):
        force_authenticate(is_staff=True)

        response = create_customer({
            'first_name': '',
            'last_name': '',
            'phone_number': '',
            'is_consumer': False
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['first_name'] is not None
        assert response.data['last_name'] is not None
        assert response.data['phone_number'] is not None

    def test_if_data_is_valid_returns_201(self, api_client, create_customer, force_authenticate):
        force_authenticate(is_staff=True)
        response = create_customer({
            'first_name': 'Jhon',
            'last_name': 'Smith',
            'phone_number': '775555555',
            'is_consumer': False
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
