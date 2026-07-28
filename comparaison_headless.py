import json
import os
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://www.lesechos.fr"

os.makedirs("screenshots", exist_ok=True)


def creer_driver(headless=False):
    options = webdriver.ChromeOptions()

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_argument(
        "--window-size=1920,1080"
    )

    
    options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )

    if headless:
        options.add_argument("--headless=new")

    return webdriver.Chrome(options=options)


def accepter_cookies(driver):
    try:
        bouton = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(., 'Accepter') "
                    "or contains(., 'Tout accepter')]"
                )
            )
        )

        bouton.click()

    except TimeoutException:
        pass


def mesurer_temps(nom_mode, headless=False):
    driver = creer_driver(headless)

    debut = time.perf_counter()

    try:
        driver.get(URL)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        accepter_cookies(driver)

        
        WebDriverWait(driver, 20).until(
            lambda navigateur: len(
                navigateur.find_elements(
                    By.TAG_NAME,
                    "a"
                )
            ) >= 10
        )

        temps = time.perf_counter() - debut

        driver.save_screenshot(
            f"screenshots/comparaison_{nom_mode}.png"
        )

        print(
            f"{nom_mode} : {temps:.2f} secondes"
        )

        return round(temps, 2)

    except TimeoutException:
        driver.save_screenshot(
            f"screenshots/erreur_{nom_mode}.png"
        )

        print(
            f"{nom_mode} : échec du chargement"
        )

        return None

    finally:
        driver.quit()


temps_normal = mesurer_temps(
    "normal",
    headless=False
)

temps_headless = mesurer_temps(
    "headless",
    headless=True
)


resultats = {
    "temps_normal_secondes": temps_normal,
    "temps_headless_secondes": temps_headless,
    "gain": None
}


if (
    temps_normal is not None
    and temps_headless is not None
    and temps_headless > 0
):
    gain = temps_normal / temps_headless

    resultats["gain"] = round(
        gain,
        2
    )

    print(
        f"Gain : {gain:.2f} fois"
    )


with open(
    "comparaison_headless.json",
    "w",
    encoding="utf-8"
) as fichier:
    json.dump(
        resultats,
        fichier,
        indent=2,
        ensure_ascii=False
    )


print(
    "\nFichier créé : comparaison_headless.json"
)