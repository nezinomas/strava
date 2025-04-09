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


class StravaData:
    _browser = None

    def __init__(self):
        self._conf = self._get_conf()
        self._browser = self._get_browser()

        self._browser.set_window_size(600, 1000)

        # self._login()
        sleep(MAX_TIME * 2)

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

        sleep(MAX_TIME)

        self._accept_cookies()

        # first stage: find email field and clid login button
        try:
            self._find_and_fill_element("input[data-cy='email']", "STRAVA_USER")
        except NoSuchElementException as e:
            raise NoSuchElementException("Email field not found.") from e

        self._press_login_button()

        # second stage: find password link and click it
        try:
            sleep(random.uniform(MIN_TIME, MAX_TIME))
            password_link = self._browser.find_element(
                By.XPATH, "//div[@data-testid='use-password-cta']/button"
            )
            password_link.click()
        except NoSuchElementException as e:
            raise NoSuchElementException("Password link not found.") from e

        # third stage: find password field and click login button
        try:
            sleep(MAX_TIME)
            self._find_and_fill_element("input[data-cy='password']", "STRAVA_PASSWORD")
        except NoSuchElementException as e:
            raise NoSuchElementException("Password field not found.") from e

        self._press_login_button()

    def _find_and_fill_element(self, input_description, conf_name):
        element = self._browser.find_element(By.CSS_SELECTOR, input_description)
        element.send_keys(self._conf[conf_name])
        sleep(random.uniform(MIN_TIME, MAX_TIME))

    def _accept_cookies(self):
        with contextlib.suppress(NoSuchElementException):
            cookie_button = self._browser.find_element(
                By.XPATH, "//button[@data-cy='accept-cookies']"
            )
            cookie_button.click()

    def _press_login_button(self):
        try:
            login_button = self._browser.find_element(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            self._browser.execute_script("arguments[0].click();", login_button)
        except NoSuchElementException as e:
            raise NoSuchElementException("Login button not found.") from e

    def _get_leaderboard_page(self):
        _id = self._conf["STRAVA_LEADERBOARD_ID"]
        self._browser.get(f"https://www.strava.com/clubs/{_id}/leaderboard")
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
            raise NoSuchElementException(txt)

        return leaderbord.get_attribute("outerHTML")

    def _get_leaderboard_for_last_week(self):
        try:
            self._browser.find_element(
                By.XPATH, "//span[@class='button last-week']"
            ).click()
            sleep(random.uniform(MIN_TIME, MAX_TIME))
        except NoSuchElementException as e:
            raise NoSuchElementException(
                "Last week leaderboard button not found."
            ) from e

        return self._get_leaderboard("For last week.")
