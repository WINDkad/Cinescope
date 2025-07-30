from constants.constants import BASE_URL, USER_ENDPOINT
from custom_requester.custom_requester import CustomRequester

class UserAPI(CustomRequester):
    def __init__(self, session):
        self.session = session
        super().__init__(session, BASE_URL)

    def get_user(self, user_locator, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"{USER_ENDPOINT}/{user_locator}",
            expected_status=expected_status
        )

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint=f"{USER_ENDPOINT}",
            data=user_data,
            expected_status=expected_status
        )