import contextlib
import random
import tomllib as toml
from pathlib import Path
from time import sleep

import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

MIN_TIME = 0.62
MAX_TIME = 5.13


class NoEmailFieldError(Exception):
    """Exception raised when email field is not found."""


class NoPasswordFieldError(Exception):
    """Exception raised when password field is not found."""


class NoLoginButtonError(Exception):
    """Exception raised when login button is not found."""


class NoLeaderboardError(Exception):
    """Exception raised when leaderboard is not found."""


class StravaData:
    _browser = None

    def __init__(self):
        self._conf = self._get_conf()
        self._browser = self._get_browser()

        self._browser.set_window_size(1600, 1000)

        # self._login()
        # sleep(MAX_TIME * 2)

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

        # first stage: find email field and clid login button
        try:
            email = self._browser.find_element(By.CSS_SELECTOR('[data-cy="email"]'))
            email.send_keys(self._conf["STRAVA_USER"])
            sleep(random.uniform(MIN_TIME, MAX_TIME))
        except NoSuchElementException as e:
            raise NoEmailFieldError("Email field not found.") from e

        try:
            login_button = self._browser.find_element(
                By.CSS_SELECTOR('[data-cy="login-button"]')
            )
            sleep(random.uniform(MIN_TIME, MAX_TIME))
            login_button.click()
        except NoSuchElementException as e:
            raise NoLoginButtonError("Login button not found.") from e

        # second stage: find password field and click login button
        try:
            password_field = self._browser.find_element(
                By.CSS_SELECTOR('[data-cy="password"]')
            )
            password_field.send_keys(self._conf["STRAVA_PASSWORD"])
            sleep(random.uniform(MIN_TIME, MAX_TIME))
        except NoSuchElementException as e:
            raise NoPasswordFieldError("Password field not found.") from e

        try:
            login_button = self._browser.findElement(
                By.CSS_SELECTOR('button[type="submit"]')
            )
            sleep(random.uniform(MIN_TIME, MAX_TIME))
            login_button.click()
        except NoSuchElementException as e:
            raise NoLoginButtonError("Login button not found.") from e

    def _accept_cookies(self):
        with contextlib.suppress(NoSuchElementException):
            cookie_button = self._browser.find_element(
                By.XPATH, "//button[@data-cy='accept-cookies']"
            )
            cookie_button.click()

    def _get_leaderboard_page(self):
        self._browser.get("https://www.strava.com/clubs/1028542/leaderboard")
        sleep(MAX_TIME)

    def _get_leaderboard(self, msg=None):
        def get_data():
            return self._browser.find_element(By.XPATH, "//div[@class='leaderboard']")

        leaderbord = None
        try:
            leaderbord = get_data()
        except NoSuchElementException:
            # self._browser.refresh()
            self._login()
            sleep(MAX_TIME)
            self._get_leaderboard_page()
            sleep(MAX_TIME)
            with contextlib.suppress(NoSuchElementException):
                leaderbord = get_data()

        if leaderbord is None:
            txt = "Leaderboard not found."
            if msg:
                txt += f" {msg}"
            raise NoLeaderboardError(txt)

        return leaderbord.get_attribute("outerHTML")

    def _get_leaderboard_for_last_week(self):
        try:
            self._browser.find_element(
                By.XPATH, "//span[@class='button last-week']"
            ).click()
            sleep(random.uniform(MIN_TIME, MAX_TIME))
        except NoSuchElementException as e:
            raise NoLeaderboardError("Last week leaderboard button not found.") from e

        return self._get_leaderboard("For last week.")
