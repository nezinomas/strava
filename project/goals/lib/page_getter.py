import contextlib
import random
from pathlib import Path
from time import sleep

import tomllib as toml
import undetected_chromedriver as uc

# from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager

MIN_TIME = 0.5
MAX_TIME = 3.5


class NoEmailFieldException(Exception):
    """Exception raised when email field is not found."""


class NoPasswordFieldException(Exception):
    """Exception raised when password field is not found."""


class NoLoginButtonException(Exception):
    """Exception raised when login button is not found."""


class NoLeaderboardException(Exception):
    """Exception raised when leaderboard is not found."""


class StravaData:
    _browser = None

    def __init__(self):
        self._conf = self._get_conf()
        self._browser = self._get_browser()

        self._browser.set_window_size(1600, 1000)

        self._login()
        self._get_leaderboard_page()

        self.this_week = self._get_leaderboard()
        self.last_week = self._get_leaderboard_for_last_week()

        self._browser.close()

    def _get_conf(self):
        conf_path = Path(__file__).absolute().parent.parent.parent.parent
        with open(conf_path / ".conf", "rb") as f:
            return toml.load(f)["strava"]

    def _get_browser(self):
        # options = Options()

        # # Setting headless mode, orherwise the browser will not open in the background when server running without GUI
        # # options.add_argument("--headless")
        # options.add_argument("--enable-javascript")

        # # Setting the user agent
        # ua = UserAgent()
        # user_agent = ua.random
        # options.add_argument(f'--user-agent={user_agent}')

        # options.add_argument("--width=1200")
        # options.add_argument("--height=800")

        # # Setting the Firefox profile
        # firefox_profile = FirefoxProfile()
        # firefox_profile.set_preference("javascript.enabled", True)
        # options.profile = firefox_profile

        # # service = Service(executable_path=self._conf["DRIVER_PATH"])
        # service = Service(executable_path=GeckoDriverManager().install())

        # return webdriver.Firefox(options=options, service=service)
        options = uc.ChromeOptions()
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--password-store=basic")
        options.add_argument("--start-maximized")
        options.add_argument("--kiosk")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        return uc.Chrome(
            headless=False,
            use_subprocess=False,
            options=options,
            driver_executable_path=self._conf["DRIVER_PATH"],
        )

    def _login(self):
        sleep(random.uniform(MIN_TIME, MAX_TIME))

        self._browser.get("https://www.strava.com/login")

        sleep(random.uniform(MIN_TIME, MAX_TIME))

        self._accept_cookies()

        fields = self._locate_login_fields()

        fields["email"].send_keys(self._conf["STRAVA_USER"])
        sleep(random.uniform(MIN_TIME, MAX_TIME))

        fields["password"].send_keys(self._conf["STRAVA_PASSWORD"])
        sleep(random.uniform(MIN_TIME, MAX_TIME))

        fields["login_button"].click()

    def _accept_cookies(self):
        with contextlib.suppress(NoSuchElementException):
            cookie_button = self._browser.find_element(
                By.XPATH, "//button[@data-cy='accept-cookies']"
            )
            cookie_button.click()

    def _locate_login_fields(self):
        field_ids = {
            "email": [
                "email",
                "desktop-email",
                "desktop-current-email",
            ],
            "password": [
                "password",
                "desktop-password",
                "desktop-current-password",
            ],
            "login_button": [
                "login-button",
                "desktop-login-button",
            ],
        }

        exceptions = {
            "email": NoEmailFieldException("Email field not found."),
            "password": NoPasswordFieldException("Password field not found."),
            "login_button": NoLoginButtonException("Login button not found."),
        }

        fields = {}
        for field_name, ids in field_ids.items():
            try:
                fields[field_name] = self._find_field(ids)
            except NoSuchElementException as e:
                raise exceptions[field_name](f"{field_name} field not found.") from e
        return fields

    def _find_field(self, ids):
        for field_id in ids:
            try:
                return self._browser.find_element(By.ID, field_id)
            except NoSuchElementException:
                continue
        raise NoSuchElementException(f"Field IDs {ids} not found.")

    def _get_leaderboard_page(self):
        sleep(random.uniform(MIN_TIME, MAX_TIME))
        self._browser.get("https://www.strava.com/clubs/1028542/leaderboard")

    def _get_leaderboard(self):
        def get_leaderboard():
            sleep(random.uniform(MIN_TIME, MAX_TIME))
            return self._browser.find_element(
                By.XPATH, "//div[@class='leaderboard']"
            )

        leaderbord = None
        try:
            leaderbord = get_leaderboard()
        except NoSuchElementException:
            self._browser.refresh()
            with contextlib.suppress(NoSuchElementException):
                leaderbord = get_leaderboard()

        if leaderbord is None:
            raise NoLeaderboardException("Leaderboard not found.")

        return leaderbord.get_attribute("outerHTML")

    def _get_leaderboard_for_last_week(self):
        self._browser.find_element(
            By.XPATH, "//span[@class='button last-week']"
        ).click()

        return self._get_leaderboard()
