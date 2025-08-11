from utils.data_generator import DataGenerator
from entities.user import User


class UserGenerator:

    @staticmethod
    def create_user_with_role(session_factory, super_admin, role):
        session = session_factory()
        password = DataGenerator.generate_random_password()
        user_data = {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": password,
            "passwordRepeat": password,
            "roles": [role.value],
            "verified": True,
            "banned": False
        }

        super_admin.api.user_api.create_user(user_data)
        user = User(user_data["email"], password, user_data["roles"], session)
        user.api.auth_api.authenticate(user.creds)
        return user
