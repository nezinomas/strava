import contextlib
import random
import tomllib as toml
from pathlib import Path
from time import sleep

import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MIN_TIME = 0.62
MAX_TIME = 5.13


class StravaData:
    _browser = None

    def __init__(self):
        self._conf = self._get_conf()
        self._browser = self._get_browser()

        try:
            self._browser.set_window_size(600, 1000)

            # self._login()
            sleep(MAX_TIME * 2)

            self._get_leaderboard_page()

            self.this_week = self._get_leaderboard("For current week.")
            self.last_week = self._get_leaderboard_for_last_week()
        finally:
            # quit() closes the browser AND ends the chromedriver process.
            # In a finally block it runs even when something above raises,
            # so a Chromium process is never left behind to leak memory.
            with contextlib.suppress(Exception):
                self._browser.quit()

    def _get_conf(self):
        self._base_dir = Path(__file__).absolute().parent.parent.parent.parent
        with open(self._base_dir / ".conf", "rb") as f:
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
        options.add_argument(f"--user-data-dir={self._conf['PROFILE']}")

        return uc.Chrome(
            headless=False,
            use_subprocess=False,
            options=options,
            driver_executable_path=self._conf["DRIVER_PATH"],
            browser_executable_path=self._conf["BROWSER_PATH"],
        )

    def _login(self):
        self._browser.get("https://www.strava.com/login")

        sleep(MAX_TIME)

        self._accept_cookies()

        # first stage: find email field and submit it
        try:
            self._find_and_fill_element("input[data-cy='email']", "STRAVA_USER")
        except NoSuchElementException as e:
            self._dump_debug("login-email")
            raise NoSuchElementException("Email field not found.") from e

        self._press_login_button()

        # second stage: Strava sometimes gates the password field behind a
        # "use password" button and sometimes shows it directly. Click the
        # button only if it is actually present -- never fail on its absence.
        sleep(random.uniform(MIN_TIME, MAX_TIME))
        self._click_use_password_cta()

        # third stage: fill the password field (waiting for it to appear) and
        # submit. If it never shows, Strava is most likely presenting a captcha
        # or "verify it's you" challenge -- the screenshot dump shows which.
        try:
            self._find_and_fill_element(
                "input[data-cy='password']", "STRAVA_PASSWORD"
            )
        except NoSuchElementException as e:
            self._dump_debug("login-password")
            raise NoSuchElementException(
                "Password field not found -- Strava may be showing a captcha "
                "or verification challenge (see the saved screenshot)."
            ) from e

        self._press_login_button()

    def _find_and_fill_element(self, input_description, conf_name, timeout=15):
        element = self._wait_for(By.CSS_SELECTOR, input_description, timeout)
        element.send_keys(self._conf[conf_name])
        sleep(random.uniform(MIN_TIME, MAX_TIME))

    def _wait_for(self, by, selector, timeout=15):
        # Wait for an element instead of relying on fixed sleeps, then reduce a
        # timeout to the NoSuchElementException the callers already handle.
        try:
            return WebDriverWait(self._browser, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException as e:
            raise NoSuchElementException(
                f"Timed out waiting for element: {selector}"
            ) from e

    def _click_use_password_cta(self):
        # After the email step Strava usually shows a "Use password instead"
        # button that reveals the password field; occasionally the field is
        # shown directly. If it's already present, nothing to do. Otherwise wait
        # for the button (it renders a beat after the page loads -- the original
        # no-wait lookup raced it) and click it. A captcha/challenge (neither
        # present) is left for the password stage to surface with a debug dump.
        if self._browser.find_elements(
            By.CSS_SELECTOR, "input[data-cy='password']"
        ):
            return
        with contextlib.suppress(NoSuchElementException):
            button = self._wait_for(
                By.XPATH,
                "//button[contains(normalize-space(.), 'Use password instead')]",
            )
            button.click()
            sleep(random.uniform(MIN_TIME, MAX_TIME))

    def _accept_cookies(self):
        with contextlib.suppress(NoSuchElementException):
            cookie_button = self._browser.find_element(
                By.XPATH, "//button[@data-cy='accept-cookies']"
            )
            cookie_button.click()

    def _press_login_button(self):
        try:
            login_button = self._wait_for(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            self._browser.execute_script("arguments[0].click();", login_button)
        except NoSuchElementException as e:
            self._dump_debug("login-button")
            raise NoSuchElementException("Login button not found.") from e

    def _dump_debug(self, label):
        # Save a screenshot + page HTML so a failed login can be diagnosed
        # without watching the (headless) browser live. Never raises. Defaults
        # to a "debug" dir next to the code (/data/sites/strava/debug); override
        # with DEBUG_DIR in .conf.
        with contextlib.suppress(Exception):
            debug_dir = Path(
                self._conf.get("DEBUG_DIR") or self._base_dir / "debug"
            )
            debug_dir.mkdir(parents=True, exist_ok=True)
            stem = debug_dir / f"strava-{label}"
            self._browser.save_screenshot(f"{stem}.png")
            Path(f"{stem}.html").write_text(
                self._browser.page_source, encoding="utf-8"
            )

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
            self._dump_debug("leaderboard")
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