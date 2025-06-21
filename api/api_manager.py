from api.auth_api import AuthAPI
from api.user_api import UserAPI
from constants import BASE_URL

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session, base_url=BASE_URL)
        self.user_api = UserAPI(session, base_url=BASE_URL)

