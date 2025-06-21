from custom_requester.custom_requester import CustomRequester

class UserAPI(CustomRequester):
    def __init__(self, session, base_url):
        super().__init__(session, base_url)

    def get_user_info(self, user_id, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    def delete_user(self, user_id, expected_status=204):
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )