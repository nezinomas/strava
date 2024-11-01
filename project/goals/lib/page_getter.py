import contextlib
import tomllib as toml
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
# from webdriver_manager.firefox import GeckoDriverManager

SLEEP_TIME = 0.25


class StravaData:
    _browser = None

    def __init__(self):
        self._conf = self._get_conf()
        self._browser = self._get_browser()

        self._login()
        self._get_leaderboard_page()

        self.this_week = self._get_html()
        self.last_week = self._get_last_week_html()

        self._browser.close()

    def _get_conf(self):
        conf_path = Path(__file__).absolute().parent.parent.parent.parent
        with open(conf_path / ".conf", "rb") as f:
            return toml.load(f)["strava"]

    def _get_browser(self):
        options = Options()

        # Setting headless mode, orherwise the browser will not open in the background when server running without GUI
        options.add_argument("--headless")
        options.add_argument("--enable-javascript")

        # Setting the Firefox profile
        firefox_profile = FirefoxProfile()
        firefox_profile.set_preference("javascript.enabled", True)
        options.profile = firefox_profile

        service = Service(executable_path=self._conf["DRIVER_PATH"])
        # service = Service(executable_path=GeckoDriverManager().install())

        return webdriver.Firefox(options=options, service=service)

    def _login(self):
        sleep(SLEEP_TIME)
        self._browser.get("https://www.strava.com/login")
        title = self._browser.execute_script("return document.title;")

        # Print the result.
        print("The title of the page is:", title)
        print(self._browser.page_source)

        sleep(SLEEP_TIME)
        with contextlib.suppress(NoSuchElementException):
            self._browser.find_element(
                By.XPATH, "//button[@class='btn-accept-cookie-banner']"
            ).click()

        sleep(SLEEP_TIME)
        self._browser.find_element(By.ID, "email").send_keys(self._conf["STRAVA_USER"])
        self._browser.find_element(By.ID, "password").send_keys(
            self._conf["STRAVA_PASSWORD"]
        )
        self._browser.find_element(By.ID, "login-button").click()

    def _get_leaderboard_page(self):
        sleep(SLEEP_TIME)
        self._browser.get("https://www.strava.com/clubs/1028542/leaderboard")

    def _get_html(self):
        return self._browser.find_element(
            By.XPATH, "//div[@class='leaderboard']"
        ).get_attribute("outerHTML")

    def _get_last_week_html(self):
        self._browser.find_element(
            By.XPATH, "//span[@class='button last-week']"
        ).click()

        sleep(SLEEP_TIME)

        return self._get_html()
