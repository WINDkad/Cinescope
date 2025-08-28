from datetime import datetime

import allure
from pytest_check import check
from sqlalchemy.orm import Session

from api.api_manager import ApiManager
from constants.roles import Roles
from db_requester.models import UserDBModel
from models.base_model import RegisterUserResponse, TestUser


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

    def test_register_user_db_session(self, api_manager: ApiManager, test_user: TestUser, db_session: Session):
        response = api_manager.auth_api.register_user(test_user)
        user_response = RegisterUserResponse(**response.json())

        users_from_db = db_session.query(UserDBModel).filter(UserDBModel.id == user_response.id)

        assert users_from_db.count() == 1, "Объект не попал в БД"
        users_from_db = users_from_db.first()
        assert users_from_db.email == test_user.email, "Email не совпадает"

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: TestUser, mocker):
        with allure.step(" Мокаем метод register_user в auth_api"):
            mock_response = RegisterUserResponse(  # Фиктивный ответ
                id="id",
                email="email@email.com",
                fullName="fullName",
                verified=True,
                banned=False,
                roles=[Roles.SUPER_ADMIN],
                createdAt=datetime.now().isoformat()
            )

            mocker.patch.object(
                api_manager.auth_api,  # Объект, который нужно замокать
                'register_user',  # Метод, который нужно замокать
                return_value=mock_response  # Фиктивный ответ
            )

        with allure.step("Вызываем метод, который должен быть замокан"):
            register_user_response = api_manager.auth_api.register_user(test_user)

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):  # обратите внимание на вложенность allure.step
                with check:
                    # Строка ниже выдаст исклющение и но выполнение теста продолжится
                    check.equal(register_user_response.fullName, "INCORRECT_NAME", "НЕСОВПАДЕНИЕ fullName")
                    check.equal(register_user_response.email, mock_response.email)

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):  # можно использовать вместо allure.step
                    check.equal(register_user_response.banned, mock_response.banned)
