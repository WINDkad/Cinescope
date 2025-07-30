import pytest
import requests

from api.api_manager import ApiManager
from constants.constants import BASE_URL, REGISTER_ENDPOINT
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from entities.user import User
from constants.roles import Roles


@pytest.fixture()
def test_user():
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }

@pytest.fixture()
def registered_user(requester, test_user):
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

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
def created_movie(admin_super_session, movie_data):
    api_manager = ApiManager(admin_super_session)
    response = api_manager.movies_api.create_movie(movie_data)
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

    super_admin = User (
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture()
def creation_user_data(test_user):
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user