import tomllib as toml
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


# get data from conf file
conf_path = Path(__file__).absolute().parent.parent.parent.parent
with open(conf_path / ".conf", "rb") as f:
    conf = toml.load(f)["strava"]


options = webdriver.ChromeOptions()
# options.add_argument('--headless')

service = Service(conf["CHROMEDRIVER_PATH"])

browser = webdriver.Chrome(service=service, options=options)
browser.get('https://www.strava.com/login')

sleep(0.5)


browser.find_element(By.XPATH, "//button[@class='btn-accept-cookie-banner']").click()

sleep(0.5)


browser.find_element(By.ID, "email").send_keys(conf["STRAVA_USER"])
browser.find_element(By.ID, "password").send_keys(conf["STRAVA_PASSWORD"])
browser.find_element(By.ID, "login-button").click()


browser.get('https://www.strava.com/clubs/1028542/leaderboard')

sleep(0.25)

# this week
text = browser.find_element(By.XPATH, "//div[@class='leaderboard']").get_attribute('outerHTML')
with open('this-week.txt', 'w', encoding='utf-8') as reader:
    reader.write(text)


# last week
browser.find_element(By.XPATH, "//span[@class='button last-week']").click()
text = browser.find_element(By.XPATH, "//div[@class='leaderboard']").get_attribute('outerHTML')
with open('last-week.txt', 'w', encoding='utf-8') as reader:
    reader.write(text)