import datetime
import time

import allure
import pytest
from pytz import timezone
from sqlalchemy.orm import Session

from conftest import super_admin_token
from db_requester.models import MovieDBModel, AccountTransactionTemplate
from utils.data_generator import DataGenerator


class TestOtherAPI:
    def test_create_delete_movie(self, api_manager, super_admin, db_session: Session, super_admin_token):
        movie_name = f"Test Movie{DataGenerator.generate_random_str(10)}"
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)

        assert movies_from_db.count() == 0, "В БД уже есть фильм с таким названием"
        movie_data = {
            "name": movie_name,
            "price": 500,
            "description": "Описание тестового фильма",
            "location": "MSK",
            "published": True,
            "genreId": 3
        }

        response = api_manager.movies_api.create_movie(movie_data)
        assert response.status_code == 201, "Фильм не создался"
        response = response.json()

        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)
        assert movies_from_db.count() == 1, "Фильм не найден"

        movie_from_db = movies_from_db.first()
        assert movie_from_db.created_at >= (datetime.datetime.now(timezone("UTC")).replace(tzinfo=None) - datetime.timedelta(minutes=5)), "Сервис выставил время создания с большой погрешностью"

        delete_response = api_manager.movies_api.delete_movie(movie_id=response["id"])
        assert delete_response.status_code == 200, "Фильм не удалился"

        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)
        assert movies_from_db.count() == 0, "Фильм не был удален из БД"

    def test_delete_movie(self, api_manager, super_admin):
        movie_id = 4076

        response = super_admin.api.movies_api.delete_movie(movie_id)
        assert response.status_code == 200

        response = api_manager.movies_api.get_movie_by_id(movie_id, expected_status=404)
        assert response.status_code == 404


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountTransactionTemplate:

    @allure.story("Корректность перевода между двумя счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_accounts_transaction_template(self, db_session: Session):
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(1, 1000)}", balance=1000)
            bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(1, 1000)}", balance=500)
            db_session.add_all([stan, bob])
            db_session.commit()

        @allure.step("Функция перевода денег: transfer_money")
        @allure.description("""
                    функция выполняющая транзакцию, имитация вызова функции на стороне тестируемого сервиса
                    и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
                    """)
        def transfer_money(session, from_account, to_account, amount):
            with allure.step("Получаем счета"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step("Проверяем, что на счете достаточно средств"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средст на счете")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохраняем изменения"):
                db_session.commit()

        # ====================================================================== Тест

        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 1000
            assert bob.balance == 500

        try:
            with allure.step("Выполняем перевод 200 единиц от stan к bob"):
                transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

            with allure.step("Провереям, что балансы изменились"):
                assert stan.balance == 800
                assert bob.balance == 700

        except Exception as e:
            with allure.step("Ошибка, откат транзакции"):
                db_session.rollback()

            pytest.fail(f"Ошибка при переводе денег {e}")

        finally:
            with allure.step("Удаляем данные для тестирования из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()