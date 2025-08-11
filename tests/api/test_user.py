import pytest

from models.baseModel import RegisterUserResponse

class TestUser:

    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        body = RegisterUserResponse(**response.json())
        assert body.id is not None, "Id не должен быть пустым"
        assert body.email == creation_user_data.email, "Email не совпадают"
        assert body.verified == True

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        response = RegisterUserResponse(**super_admin.api.user_api.create_user(creation_user_data).json())
        response_id = RegisterUserResponse(**super_admin.api.user_api.get_user(response.id).json())
        response_email = RegisterUserResponse(**super_admin.api.user_api.get_user(response.email).json())

        assert response_id == response_email, "Ответы должны быть одинаковыми"
        assert response_id.email == creation_user_data.email
        assert response_id.verified is True

    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)