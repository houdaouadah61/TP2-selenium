import json
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


FICHIER_DOCTOLIB = "doctolib.json"
FICHIER_REFERENCE = "defi3_reference.json"
FICHIER_RESULTAT = "defi3_resultat.json"

os.makedirs("screenshots", exist_ok=True)


def lire_premier_medecin():
    

    with open(
        FICHIER_DOCTOLIB,
        "r",
        encoding="utf-8"
    ) as fichier:
        donnees = json.load(fichier)

    if isinstance(donnees, list):
        medecins = donnees

    elif isinstance(donnees, dict):
        medecins = (
            donnees.get("medecins")
            or donnees.get("docteurs")
            or donnees.get("resultats")
            or []
        )

    else:
        medecins = []

    for medecin in medecins:
        url = medecin.get("url_fiche", "")

        if url.startswith("http"):
            return medecin

    raise RuntimeError(
        "Aucune URL valide trouvée dans doctolib.json."
    )


def accepter_cookies(driver):
    

    try:
        bouton = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(., 'Tout accepter') "
                    "or contains(., 'Accepter')]"
                )
            )
        )

        bouton.click()
        print("Cookies acceptés.")

    except TimeoutException:
        print("Aucune bannière de cookies détectée.")


def chercher_texte(driver, selecteurs):
    

    for tentative in range(2):

        for selecteur in selecteurs:
            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selecteur
            )

            for element in elements:

                try:
                    texte = " ".join(
                        element.text.split()
                    )

                    if texte:
                        return texte, selecteur

                except StaleElementReferenceException:
                    continue

        try:
            WebDriverWait(driver, 3).until(
                lambda navigateur:
                navigateur.execute_script(
                    "return document.readyState"
                ) == "complete"
            )

        except TimeoutException:
            pass

    return "n/a", "aucun"


def chercher_adresse(driver):
    

    adresse, selecteur = chercher_texte(
        driver,
        [
            "address",
            "[data-test*='address']",
            "[class*='address']"
        ]
    )

    if adresse != "n/a":
        return adresse, selecteur

    try:
        body = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        texte_page = body.text

    except StaleElementReferenceException:
        texte_page = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

    lignes = [
        ligne.strip()
        for ligne in texte_page.splitlines()
        if ligne.strip()
    ]

    for index, ligne in enumerate(lignes):

        if index > 0 and re.match(
            r"^\d{5}\s+.+",
            ligne
        ):
            adresse = (
                f"{lignes[index - 1]}, {ligne}"
            )

            return adresse, "recherche du code postal"

    return "n/a", "aucun"


def separer_nom_specialite(medecin):
    

    nom_specialite = medecin.get(
        "nom_specialite",
        ""
    )

    if " - " in nom_specialite:
        nom, specialite = nom_specialite.split(
            " - ",
            1
        )

        return nom.strip(), specialite.strip()

    return nom_specialite.strip(), ""


def comparer_selecteurs(resultat):
    

    if not os.path.exists(FICHIER_REFERENCE):

        with open(
            FICHIER_REFERENCE,
            "w",
            encoding="utf-8"
        ) as fichier:
            json.dump(
                resultat,
                fichier,
                indent=2,
                ensure_ascii=False
            )

        print("Fichier de référence créé.")

        return []

    with open(
        FICHIER_REFERENCE,
        "r",
        encoding="utf-8"
    ) as fichier:
        reference = json.load(fichier)

    anciens_selecteurs = reference.get(
        "selecteurs_utilises",
        {}
    )

    changements = []

    for champ, selecteur_actuel in resultat[
        "selecteurs_utilises"
    ].items():

        ancien_selecteur = anciens_selecteurs.get(
            champ
        )

        if ancien_selecteur != selecteur_actuel:

            changements.append(
                {
                    "champ": champ,
                    "avant": ancien_selecteur,
                    "maintenant": selecteur_actuel
                }
            )

    return changements


driver = webdriver.Chrome()
driver.maximize_window()

try:
    medecin_json = lire_premier_medecin()

    url_medecin = medecin_json["url_fiche"]

    print("URL utilisée :", url_medecin)

    driver.get(url_medecin)

    accepter_cookies(driver)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        )
    )

    nom, selecteur_nom = chercher_texte(
        driver,
        [
            "h1",
            "[data-test*='name']",
            "[class*='name']"
        ]
    )

    specialite, selecteur_specialite = (
        chercher_texte(
            driver,
            [
                "[data-test*='speciality']",
                "[class*='speciality']",
                "[class*='specialty']"
            ]
        )
    )

    nom_json, specialite_json = (
        separer_nom_specialite(
            medecin_json
        )
    )

    if nom == "n/a" and nom_json:
        nom = nom_json
        selecteur_nom = "valeur de doctolib.json"

    if specialite == "n/a" and specialite_json:
        specialite = specialite_json
        selecteur_specialite = (
            "valeur de doctolib.json"
        )

    adresse, selecteur_adresse = (
        chercher_adresse(driver)
    )

    if adresse == "n/a":

        adresse_json = medecin_json.get(
            "adresse",
            ""
        )

        if adresse_json:
            adresse = adresse_json
            selecteur_adresse = (
                "valeur de doctolib.json"
            )

    resultat = {
        "date_test": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "url_fiche": url_medecin,
        "donnees": {
            "nom": nom,
            "specialite": specialite,
            "adresse": adresse
        },
        "selecteurs_utilises": {
            "nom": selecteur_nom,
            "specialite": selecteur_specialite,
            "adresse": selecteur_adresse
        }
    }

    changements = comparer_selecteurs(
        resultat
    )

    resultat["changements_detectes"] = (
        changements
    )

    with open(
        FICHIER_RESULTAT,
        "w",
        encoding="utf-8"
    ) as fichier:
        json.dump(
            resultat,
            fichier,
            indent=2,
            ensure_ascii=False
        )

    print("\nRésultat :")

    print(
        json.dumps(
            resultat,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        "\nNombre de sélecteurs modifiés :",
        len(changements)
    )

except Exception as erreur:

    driver.save_screenshot(
        "screenshots/defi3_erreur.png"
    )

    resultat_erreur = {
        "date_test": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "erreur": type(erreur).__name__,
        "message": str(erreur)
    }

    with open(
        FICHIER_RESULTAT,
        "w",
        encoding="utf-8"
    ) as fichier:
        json.dump(
            resultat_erreur,
            fichier,
            indent=2,
            ensure_ascii=False
        )

    print("Erreur :", erreur)

finally:
    driver.quit()


print("\nFichier créé : defi3_resultat.json")