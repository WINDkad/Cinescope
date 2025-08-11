from api.api_manager import ApiManager
from models.baseModel import RegisterUserResponse, TestUser


class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user: TestUser):
        response = api_manager.auth_api.register_user(user_data=test_user)
        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email == test_user.email, "Email не совпадает"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user: TestUser):
        login_data = {
            "email": registered_user.email,
            "password": registered_user.password
        }

        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user.email, "Email не совпадает"