import json
import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://bot.sannysoft.com"

os.makedirs("screenshots", exist_ok=True)


def attendre_resultats(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        WebDriverWait(driver, 20).until(
            lambda navigateur: len(
                navigateur.find_element(
                    By.TAG_NAME,
                    "body"
                ).text
            ) > 100
        )

    except TimeoutException:
        print("La page a mis trop de temps à charger.")


def lancer_test(nom, mode_stealth=False, headless=False):
    options = webdriver.ChromeOptions()

    if mode_stealth:
        options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )

        options.add_experimental_option(
            "excludeSwitches",
            ["enable-automation"]
        )

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,3000")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)

        attendre_resultats(driver)

        webdriver_detecte = driver.execute_script(
            "return navigator.webdriver"
        )

        user_agent = driver.execute_script(
            "return navigator.userAgent"
        )

        driver.save_screenshot(
            f"screenshots/bot_{nom}.png"
        )

        print(
            f"{nom} : navigator.webdriver = "
            f"{webdriver_detecte}"
        )

        return {
            "test": nom,
            "navigator_webdriver": webdriver_detecte,
            "user_agent": user_agent,
            "capture": f"screenshots/bot_{nom}.png"
        }

    finally:
        driver.quit()


resultats = []

resultats.append(
    lancer_test(
        nom="normal",
        mode_stealth=False,
        headless=False
    )
)

resultats.append(
    lancer_test(
        nom="stealth",
        mode_stealth=True,
        headless=False
    )
)

resultats.append(
    lancer_test(
        nom="headless",
        mode_stealth=True,
        headless=True
    )
)


with open(
    "defi2_resultats.json",
    "w",
    encoding="utf-8"
) as fichier:
    json.dump(
        resultats,
        fichier,
        indent=2,
        ensure_ascii=False
    )


print("\nDéfi 2 terminé.")
print("Captures créées :")
print("- screenshots/bot_normal.png")
print("- screenshots/bot_stealth.png")
print("- screenshots/bot_headless.png")
print("- defi2_resultats.json")