from conftest import super_admin, created_movie
from utils.data_generator import DataGenerator
import pytest

class TestMoviesAPI:
    """Позитивные тесты"""

    def test_create_movie(self, super_admin, movie_data):
        response = super_admin.api.movies_api.create_movie(movie_data).json()
        assert response.get("name") == movie_data["name"], "Имя не совпадает"

    def test_get_movie(self, super_admin):
        response = super_admin.api.movies_api.get_movies()
        assert response.status_code == 200, "Фильмы не найден"

    def test_get_movie_by_id(self, super_admin, created_movie):
        movie_id = created_movie["id"]

        response = super_admin.api.movies_api.get_movie_by_id(movie_id)
        assert response.status_code == 200, "Фильм не найден"

    def test_delete_movie(self, super_admin, created_movie):
        movie_id = created_movie["id"]

        response = super_admin.api.movies_api.delete_movie(movie_id)
        assert response.status_code == 200, "Фильм не удалился"

        response = super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)
        assert response.status_code == 404, "Фильм найден"

    def test_update_movie(self, super_admin, update_data, created_movie):
        movie_id = created_movie["id"]

        response = super_admin.api.movies_api.update_movie(movie_id, update_data)
        assert response.status_code == 200, "Ошибка при обновлении данных"

    def test_get_movie_by_common_user(self, common_user):
        response = common_user.api.movies_api.get_movies()
        assert response.status_code == 200, "Фильмы не найдены"

    @pytest.mark.parametrize(
        "params",
        [
            {"minPrice": 100, "maxPrice": 500},
            {"locations": "MSK"},
            {"genreId": 1},
            {"minPrice": 200, "maxPrice": 700, "locations": "SPB", "genreId": 2}
        ],
        ids=[
            "Фильтрация по цене, от 100 до 500",
            "Фильтрация по городу, только МСК",
            "Фильтрация по genreId 1",
            "Фильрация по всем параметрам"
        ]
    )
    def test_get_movies_by_params(self, super_admin, params):
        response = super_admin.api.movies_api.get_movies(params)
        assert response.status_code == 200

        movies = response.json().get("movies", [])
        for movie in movies:
            if "minPrice" in params:
                assert movie["price"] >= params["minPrice"]
            if "maxPrice" in params:
                assert movie["price"] <= params["maxPrice"]
            if "locations" in params:
                assert movie["location"] in params["locations"]
            if "genreId" in params:
                assert movie["genreId"] == params["genreId"]

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "user, expected_status",
        [
            ("super_admin", 200),
            ("admin", 403),
            ("common_user", 403)
        ],
        ids=[
            "Удаление супер админом разрешено",
            "Удаление админом запрещено",
            "Удаление обычным пользователем запрещено"
        ]
    )
    def test_delete_movie_by_role(self, super_admin, admin, common_user, expected_status, user, movie_data):
        response = super_admin.api.movies_api.create_movie(movie_data)
        assert response.status_code == 201
        movie_id = response.json().get("id")

        roles = {
            "super_admin": super_admin,
            "admin": admin,
            "common_user": common_user
        }
        role = roles[user]

        response = role.api.movies_api.delete_movie(movie_id, expected_status)
        assert response.status_code == expected_status

        if expected_status == 200:
            response = role.api.movies_api.get_movie_by_id(movie_id, expected_status=404)
            assert response.status_code == 404

class TestMoviesAPINegative:
    """Негативные тесты"""

    def test_create_movie_conflict(self, super_admin):
        movie_name = "Witcher"

        movie_data = {
            "name": movie_name,
            "imageUrl": "https://example.com/image.png",
            "price": 100,
            "description": "Описание фильма",
            "location": "SPB",
            "published": True,
            "genreId": 1
        }

        response = super_admin.api.movies_api.create_movie(movie_data, expected_status=409)
        assert response.status_code == 409, "Фильм создался"

    def test_get_movie_by_invalid_id(self, super_admin):
        response = super_admin.api.movies_api.get_movie_by_id(DataGenerator.generate_random_int(42000, 100000), expected_status=404)
        assert response.status_code == 404, "Фильм найден"

    def test_delete_by_invalid_id(self, super_admin):
        response = super_admin.api.movies_api.delete_movie(DataGenerator.generate_random_int(42000, 100000), expected_status=404)
        assert response.status_code == 404, "Фильм удалился"

    def test_update_by_invalid_data(self, super_admin, created_movie):
        movie_id = created_movie["id"]

        data = {
        "name": DataGenerator.generate_random_int(1, 100),
        "price": -100,
        "imageUrl": "https://example.com/image.png",
        "description": DataGenerator.generate_random_sentence(5),
        "location": "MSK",
        "published": DataGenerator.generate_random_sentence(3),
        "genreId": DataGenerator.generate_random_boolean()
        }

        response = super_admin.api.movies_api.update_movie(movie_id, data, expected_status=400)
        assert response.status_code == 400, "Данные обновлены"

    @pytest.mark.slow
    def test_create_movie_by_user(self, common_user, movie_data):
        response = common_user.api.movies_api.create_movie(movie_data, expected_status=403)
        assert response.status_code == 403, "Фильм создался"