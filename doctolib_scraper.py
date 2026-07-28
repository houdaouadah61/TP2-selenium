import json
import os
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://www.doctolib.fr/dermatologue/Montpellier"
SELECTEUR_LIENS = "//a[contains(@href, '/dermatologue/montpellier/')]"
NOMBRE_MAX_MEDECINS = 10

os.makedirs("screenshots", exist_ok=True)


def accepter_cookies(driver):
    try:
        bouton = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(., 'Tout accepter') "
                    "or contains(., 'Accepter')]",
                )
            )
        )
        bouton.click()
        print("Cookies acceptés.")

    except TimeoutException:
        print("Aucune bannière de cookies détectée.")


def attendre_resultats(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, SELECTEUR_LIENS)
            )
        )
        print("Résultats chargés.")

    except TimeoutException as erreur:
        driver.save_screenshot(
            "screenshots/doctolib_resultats_erreur.png"
        )
        raise RuntimeError(
            "Les résultats Doctolib ne se sont pas chargés."
        ) from erreur


def scroller_page(driver):
    for numero in range(3):
        ancien_nombre = len(
            driver.find_elements(By.XPATH, SELECTEUR_LIENS)
        )

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        try:
            WebDriverWait(driver, 4).until(
                lambda navigateur: len(
                    navigateur.find_elements(
                        By.XPATH,
                        SELECTEUR_LIENS
                    )
                ) > ancien_nombre
            )
        except TimeoutException:
            pass

        nouveau_nombre = len(
            driver.find_elements(By.XPATH, SELECTEUR_LIENS)
        )

        print(
            f"Scroll {numero + 1}/3 : "
            f"{nouveau_nombre} fiche(s) détectée(s)"
        )


def trouver_carte(driver, lien):
    
    

    return driver.execute_script(
        """
        let bloc = arguments[0];
        let blocSecours = null;

        while (bloc && bloc !== document.body) {
            const texte = (bloc.innerText || "").trim();

            const contientAdresse =
                /\\b\\d{5}\\b/.test(texte);

            const contientDisponibilite =
                /aucune disponibilité|à partir du|prochaine disponibilité|matin|après-midi|\\b\\d{1,2}[h:]\\d{2}\\b/i
                .test(texte);

            if (
                !blocSecours &&
                contientAdresse &&
                texte.length < 2500
            ) {
                blocSecours = bloc;
            }

            if (
                contientAdresse &&
                contientDisponibilite &&
                texte.length < 3000
            ) {
                return bloc;
            }

            bloc = bloc.parentElement;
        }

        return blocSecours || arguments[0].parentElement;
        """,
        lien,
    )

def extraire_creneaux_carte(carte):
    

    texte_carte = carte.text

    
    elements = carte.find_elements(
        By.CSS_SELECTOR,
        "button, a, time, [role='button']"
    )

    textes = [texte_carte]

    for element in elements:
        textes.append(element.text or "")
        textes.append(
            element.get_attribute("aria-label") or ""
        )
        textes.append(
            element.get_attribute("title") or ""
        )

    texte_complet = "\n".join(textes)

    
    heures = re.findall(
        r"\b(?:[01]?\d|2[0-3])(?:h|:)[0-5]\d\b",
        texte_complet
    )

    creneaux = []

    for heure in heures:
        if heure not in creneaux:
            creneaux.append(heure)

        if len(creneaux) == 3:
            return creneaux

    lignes = [
        " ".join(ligne.split())
        for ligne in texte_complet.splitlines()
        if ligne.strip()
    ]

    
    for ligne in lignes:
        if re.search(
            r"à partir du",
            ligne,
            re.IGNORECASE
        ):
            if ligne not in creneaux:
                creneaux.append(ligne)

        elif re.search(
            r"\b(?:lun|mar|mer|jeu|ven|sam|dim)\.?\s+\d{1,2}.*"
            r"(?:matin|après-midi)",
            ligne,
            re.IGNORECASE
        ):
            if ligne not in creneaux:
                creneaux.append(ligne)

        if len(creneaux) == 3:
            return creneaux

    # Une liste vide signifie réellement
    # qu'aucun créneau n'est affiché.
    return []


def recuperer_fiches_resultats(driver):
    
    liens = driver.find_elements(
        By.XPATH,
        SELECTEUR_LIENS
    )

    fiches = []
    urls_connues = set()

    for lien in liens:
        url = lien.get_attribute("href")

        if not url:
            continue

        url_unique = url.split("?")[0]

        if url_unique in urls_connues:
            continue

        try:
            carte = trouver_carte(driver, lien)
            creneaux = extraire_creneaux_carte(carte)

        except WebDriverException:
            creneaux = ["Disponibilité non affichée"]

        fiches.append(
            {
                "url": url,
                "prochains_creneaux": creneaux,
            }
        )

        urls_connues.add(url_unique)

        if len(fiches) == NOMBRE_MAX_MEDECINS:
            break

    return fiches


def extraire_specialite(driver):
    titre_page = driver.title

    if "," in titre_page:
        partie = titre_page.split(",", 1)[1]
        specialite = partie.split(" à ", 1)[0]
        return specialite.strip()

    return "Non trouvée"


def extraire_adresse(texte_page):
    lignes = [
        ligne.strip()
        for ligne in texte_page.splitlines()
        if ligne.strip()
    ]

    for index, ligne in enumerate(lignes):
        if re.match(r"^\d{5}\s+.+", ligne) and index > 0:
            return f"{lignes[index - 1]}, {ligne}"

    return "Non trouvée"


def extraire_type_consultation(texte_page):
    texte = texte_page.lower()

    video = (
        "consultation vidéo" in texte
        or "consultation video" in texte
        or "téléconsultation" in texte
    )

    cabinet = (
        "cabinet" in texte
        or "sur place" in texte
    )

    if video and cabinet:
        return "Cabinet et Vidéo"

    if video:
        return "Vidéo"

    return "Cabinet"


def extraire_fiche(driver, fiche, numero):
    url = fiche["url"]

    try:
        driver.get(url)

        nom = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.TAG_NAME, "h1")
            )
        ).text.strip()

        texte_page = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        medecin = {
            "nom_specialite": (
                f"{nom} - {extraire_specialite(driver)}"
            ),
            "adresse": extraire_adresse(texte_page),
            "type_consultation": (
                extraire_type_consultation(texte_page)
            ),
            "prochains_creneaux": (
                fiche["prochains_creneaux"]
            ),
            "url_fiche": url,
        }

        print(
            f"{numero} - {nom} extrait : "
            f"{fiche['prochains_creneaux']}"
        )

        return medecin

    except Exception as erreur:
        chemin = (
            f"screenshots/"
            f"doctolib_fiche_{numero}_erreur.png"
        )

        try:
            driver.save_screenshot(chemin)
        except WebDriverException:
            pass

        print(
            f"Erreur sur la fiche {numero} :",
            erreur
        )

        return None


options = webdriver.ChromeOptions()

options.add_argument(
    "--disable-blink-features=AutomationControlled"
)

options.add_experimental_option(
    "excludeSwitches",
    ["enable-automation"]
)

driver = webdriver.Chrome(options=options)
driver.maximize_window()

medecins = []

try:
    driver.get(URL)

    accepter_cookies(driver)
    attendre_resultats(driver)
    scroller_page(driver)

    fiches = recuperer_fiches_resultats(driver)

    print(
        f"{len(fiches)} fiche(s) seront visitées."
    )

    for numero, fiche in enumerate(fiches, start=1):
        medecin = extraire_fiche(
            driver,
            fiche,
            numero
        )

        if medecin is not None:
            medecins.append(medecin)

finally:
    driver.quit()


with open(
    "doctolib.json",
    "w",
    encoding="utf-8"
) as fichier:
    json.dump(
        medecins,
        fichier,
        indent=2,
        ensure_ascii=False
    )


print(
    f"{len(medecins)} médecin(s) "
    "exporté(s) dans doctolib.json."
)