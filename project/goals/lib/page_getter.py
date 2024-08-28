import tomllib as toml
from pathlib import Path
from time import sleep

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def get_leaderboard():
    # get data from conf file
    # conf_path = Path(__file__).absolute().parent.parent.parent.parent
    # with open(conf_path / ".conf", "rb") as f:
    #     conf = toml.load(f)["strava"]

    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options = Options()
    # options.add_argument('--headless')
    # print(f'--------------------------->\n{conf["CHROMEDRIVER_PATH"]=}\n')
    # service = FirefoxService(conf["CHROMEDRIVER_PATH"])

    service = FirefoxService(options=options, executable_path=GeckoDriverManager().install())
    browser = webdriver.Firefox(service=service)

    # browser = webdriver.Firefox(service=service, options=options)
    browser.get('https://www.strava.com/login')

    sleep(0.25)

    browser.find_element(By.XPATH, "//button[@class='btn-accept-cookie-banner']").click()

    sleep(0.25)

    browser.find_element(By.ID, "email").send_keys(conf["STRAVA_USER"])
    browser.find_element(By.ID, "password").send_keys(conf["STRAVA_PASSWORD"])
    browser.find_element(By.ID, "login-button").click()

    browser.get('https://www.strava.com/clubs/1028542/leaderboard')

    sleep(0.25)

    return browser


def get_leaderboard_html(browser):
    return browser.find_element(By.XPATH, "//div[@class='leaderboard']").get_attribute('outerHTML')


def get_last_week_leaderboard_html(browser):
    browser.find_element(By.XPATH, "//span[@class='button last-week']").click()

    sleep(0.25)

    return get_leaderboard_html(browser)
