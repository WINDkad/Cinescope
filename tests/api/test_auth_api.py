import pytest
import requests
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }

        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data, "accessToken отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

    def test_auth_invalid_password(self, requester, registered_user):
        login_data = {
            "email": registered_user["email"],
            "password": "123412343"
        }
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=login_data,
            expected_status=400
        )

    def test_auth_invalid_email(self, requester, registered_user):
        login_data = {
            "email": "12312@gmail.com",
            "password": registered_user["password"]
        }
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=login_data,
            expected_status=400
        )

    def test_auth_empty_login_data(self, requester, registered_user):
        login_data = {}
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=login_data,
            expected_status=400
        )