import allure
from playwright.sync_api import Page


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator, text: str):
        locator.fill(text)

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator: str):
        self.page.click(locator)

    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url: str):
        self.page.wait_for_url(url)
        assert self.page.url == url, "Редирект на домашнюю страницу не произошел"

    @allure.step("Получение текста элемента: {locator}")
    def get_element_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content()

    @allure.step("Ожидание появления или исчезновения элемента: {locator}, state = {state}")
    def wait_for_element(self, locator: str, state: str = "visible"):
        self.page.locator(locator).wait_for(state=state)

    @allure.step("Скриншот текущей страиницы")
    def make_screenshot_and_attach_to_allure(self):
        screenshot_path = "screenshot.png"
        self.page.screenshot(path=screenshot_path, full_page=True)

        with open(screenshot_path, "rb") as file:
            allure.attach(file.read(), name="Screenshot after redirect", attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения c текстом: {text}")
    def check_pop_up_element_with_text(self, text: str) -> bool:

        with allure.step("Проверка появления алерта с текстом: '{text}'"):
            notification_locator = self.page.get_by_text(text)
            notification_locator.wait_for(state="visible")
            assert notification_locator.is_visible(), "Уведомление не появилось"

        with allure.step("Проверка исчезновения алерта с текстом: '{text}'"):
            notification_locator.wait_for(state="hidden")
            assert notification_locator.is_visible() == False, "Уведомление не исчезло"


class BasePage(PageAction):
    def __init__(self, page: Page):
        super().__init__(page)
        self.home_url = "https://dev-cinescope.coconutqa.ru/"
        self.home_button = page.get_by_role("link", name="Cinescope") #
        self.all_movies_button = page.get_by_role("link", name="Все фильмы")

    @allure.step("Переход на главную страницу, из шапки сайта")
    def go_to_home_page(self):
        self.home_button.click()
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Переход на страницу 'Все фильмы, из шапки сайта'")
    def go_to_all_movies(self):
        self.all_movies_button.click()
        self.wait_redirect_for_url(f"{self.home_url}movies")

class CinescopRegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        self.full_name_input = page.get_by_role("textbox", name="Имя Фамилия Отчество")
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль", exact=True)
        self.repeat_password_input = page.get_by_role("textbox", name="Повторите пароль")

        self.register_button = page.get_by_role("button", name="Зарегистрироваться")
        self.sign_button = page.get_by_role("link", name="Войти")

    def open(self):
        self.open_url(self.url)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Полный процесс регистрации"""
        self.enter_text_to_element(self.full_name_input, full_name)
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.repeat_password_input, confirm_password)

        self.register_button.click()

    def assert_was_redirect_to_login_page(self):
        self.wait_redirect_for_url(f"{self.home_url}login")

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Подтвердите свою почту")


class CinescopLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль")

        self.login_button = page.get_by_role("button", name="Войти")
        self.register_button = page.get_by_role("link", name="Зарегистрироваться")

    def open(self):
        self.open_url(self.url)

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)

        self.login_button.click()

    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")