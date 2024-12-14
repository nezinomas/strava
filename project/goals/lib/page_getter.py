import contextlib
import random
from pathlib import Path
from time import sleep

import tomllib as toml
import undetected_chromedriver as uc

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


MIN_TIME = 0.5
MAX_TIME = 5.0


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

        self.this_week = self._get_leaderboard("For current week.")
        self.last_week = self._get_leaderboard_for_last_week()

        self._browser.close()

    def _get_conf(self):
        conf_path = Path(__file__).absolute().parent.parent.parent.parent
        with open(conf_path / ".conf", "rb") as f:
            return toml.load(f)["strava"]

    def _get_browser(self):
        options = uc.ChromeOptions()
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--password-store=basic")
        options.add_argument("--start-maximized")
        options.add_argument("--kiosk")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-data-dir=chromium")

        return uc.Chrome(
            headless=False,
            use_subprocess=False,
            options=options,
            driver_executable_path=self._conf["DRIVER_PATH"],
        )

    def _login(self):
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
        page = "https://www.strava.com/clubs/1028542/leaderboard"
        self._browser.get(page)
        sleep(MAX_TIME * 2)

        # sometimes strava sends you to the signup page???
        signup = None
        with contextlib.suppress(NoSuchElementException):
            signup = self._browser.find_element(
                By.ID, "sign-up-modal-signup-button"
            )

        if signup:
            self._login()

        self._browser.get(page)
        sleep(MAX_TIME * 2)

    def _get_leaderboard(self, msg = None):
        def get_data():
            return self._browser.find_element(
                By.XPATH, "//div[@class='leaderboard']"
            )

        leaderbord = None
        try:
            leaderbord = get_data()
        except NoSuchElementException:
            self._browser.refresh()
            sleep(MAX_TIME)
            with contextlib.suppress(NoSuchElementException):
                leaderbord = get_data()

        if leaderbord is None:
            txt = "Leaderboard not found."
            if msg:
                txt += f" {msg}"
            raise NoLeaderboardException(txt)

        return leaderbord.get_attribute("outerHTML")

    def _get_leaderboard_for_last_week(self):
        try:
            self._browser.find_element(
                By.XPATH, "//span[@class='button last-week']"
            ).click()
            sleep(random.uniform(MIN_TIME, MAX_TIME))
        except NoSuchElementException as e:
            raise NoLeaderboardException("Last week leaderboard button not found.") from e

        return self._get_leaderboard("For last week.")
