import pytest
import requests

from api.api_manager import ApiManager
from constants.constants import BASE_URL, REGISTER_ENDPOINT
from resources.user_creds import SuperAdminCreds
from tests.api.test_user import TestUser
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from entities.user import User
from constants.roles import Roles
from utils.user_generator import UserGenerator
from models.baseModel import TestUser


@pytest.fixture()
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )

@pytest.fixture()
def registered_user(requester, test_user: TestUser) -> TestUser:
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user.model_dump(),
        expected_status=201
    )

    response_data = response.json()
    return test_user.model_copy(update={
        "id": response_data["id"]
    })

@pytest.fixture(scope="session")
def admin_super_session():
    session = requests.Session()
    requester = CustomRequester(session, base_url=BASE_URL)

    login_data = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

    response = requester.send_request(method="POST", endpoint="/login", data=login_data)
    token = response.json().get("accessToken")
    assert token is not None, "Токен не найден в ответе"

    session.headers.update({"Authorization": f"Bearer {token}"})
    return session

@pytest.fixture()
def movie_data():
    return {
        "name": DataGenerator.generate_random_name(),
        "imageUrl": "https://example.com/image.png",
        "price": DataGenerator.generate_random_int(1, 1000),
        "description": DataGenerator.generate_random_sentence(5),
        "location": "MSK",
        "published": DataGenerator.generate_random_boolean(),
        "genreId": DataGenerator.generate_random_int(1, 2)
    }

@pytest.fixture()
def update_data():
    return {
        "name": DataGenerator.generate_random_name(),
        "imageUrl": "https://example.com/image.png",
        "price": DataGenerator.generate_random_int(1, 1000),
        "description": DataGenerator.generate_random_sentence(5),
        "location": "MSK",
        "published": DataGenerator.generate_random_boolean(),
        "genreId": DataGenerator.generate_random_int(1, 2)
    }

@pytest.fixture()
def created_movie(super_admin, movie_data):
    response = super_admin.api.movies_api.create_movie(movie_data)
    return response.json()

@pytest.fixture(scope="session")
def requester():
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)

@pytest.fixture()
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture()
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture()
def creation_user_data(test_user: TestUser) -> TestUser:
    return test_user.model_copy(update={
        "verified": True,
        "banned": False,
    })

@pytest.fixture()
def common_user(user_session, super_admin):
    return UserGenerator.create_user_with_role(user_session, super_admin, Roles.USER)

@pytest.fixture()
def admin(user_session, super_admin):
    return UserGenerator.create_user_with_role(user_session, super_admin, Roles.ADMIN)