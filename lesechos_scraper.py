import json
import os
import re
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://www.lesechos.fr"
MAX_ARTICLES = 15

os.makedirs("screenshots", exist_ok=True)

def tester_requests():
    try:
        reponse = requests.get(
            URL,
            headers={
                "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)"
            },
            timeout=10
        )

        soup = BeautifulSoup(reponse.text, "lxml")
        titres = soup.select("h2, h3")

        print(
            f"Test requests : {len(titres)} "
            "balise(s) de titre trouvée(s)."
        )

        if len(titres) == 0:
            print(
                "Requests ne suffit pas : "
                "Selenium est nécessaire."
            )
        else:
            print(
                "Requests trouve du contenu, mais Selenium "
                "est conservé pour les données dynamiques."
            )

    except requests.RequestException as erreur:
        print("Erreur requests :", erreur)



def creer_driver(headless=False):
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(40)

    if not headless:
        driver.maximize_window()

    return driver




def accepter_cookies(driver):
    try:
        bouton = WebDriverWait(driver, 5).until(
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


def faire_capture(driver, nom):
    chemin = f"screenshots/{nom}.png"

    try:
        driver.save_screenshot(chemin)
        print("Capture enregistrée :", chemin)
    except WebDriverException:
        print("Capture impossible.")



def mesurer_chargement(headless):
    driver = creer_driver(headless=headless)
    debut = time.perf_counter()

    try:
        driver.get(URL)

        WebDriverWait(driver, 20).until(
            lambda navigateur: navigateur.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        return time.perf_counter() - debut

    except (TimeoutException, WebDriverException):
        nom = (
            "lesechos_headless_erreur"
            if headless
            else "lesechos_normal_erreur"
        )

        faire_capture(driver, nom)
        return None

    finally:
        try:
            driver.quit()
        except WebDriverException:
            pass

def nettoyer_texte(texte):
    return " ".join((texte or "").split())


def nettoyer_titre(titre):
    titre = re.sub(
        r"\bPREMIUM\b",
        "",
        titre,
        flags=re.IGNORECASE
    )

    return nettoyer_texte(titre)


def est_url_article(url, titre):
    if not url or "lesechos.fr" not in url:
        return False

    chemin = urlparse(url).path.strip("/")

    if not chemin:
        return False

    dernier_morceau = chemin.split("/")[-1]

    pages_a_exclure = [
        "recherche",
        "abonnement",
        "connexion",
        "newsletter",
        "podcasts",
        "videos"
    ]

    if any(mot in chemin.lower() for mot in pages_a_exclure):
        return False

    return (
        len(titre) >= 20
        and len(dernier_morceau) >= 25
        and "-" in dernier_morceau
    )


def recuperer_articles_une(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "main h2, main h3")
            )
        )

    except TimeoutException as erreur:
        faire_capture(
            driver,
            "lesechos_articles_introuvables"
        )

        raise RuntimeError(
            "Les titres de la une ne sont pas chargés."
        ) from erreur

    titres_html = driver.find_elements(
        By.CSS_SELECTOR,
        "main h2, main h3"
    )

    articles = []
    urls_connues = set()

    for element_titre in titres_html:
        titre_brut = nettoyer_texte(element_titre.text)
        titre = nettoyer_titre(titre_brut)

        if not titre:
            continue

        lien = driver.execute_script(
            """
            return arguments[0].closest('a')
                || arguments[0].querySelector('a')
                || arguments[0].parentElement.closest('a');
            """,
            element_titre
        )

        if lien is None:
            continue

        url = lien.get_attribute("href")

        if not est_url_article(url, titre):
            continue

        url_sans_parametres = url.split("?")[0]

        if url_sans_parametres in urls_connues:
            continue

        premium_une = "premium" in titre_brut.lower()

        articles.append(
            {
                "titre": titre,
                "rubrique": "",
                "chapeau": "",
                "heure_publi": "",
                "premium": premium_une,
                "url": url_sans_parametres
            }
        )

        urls_connues.add(url_sans_parametres)

        if len(articles) == MAX_ARTICLES:
            break

    return articles

def trouver_premier_texte(driver, selecteurs, longueur_min=1):
    for selecteur in selecteurs:
        elements = driver.find_elements(
            By.CSS_SELECTOR,
            selecteur
        )

        for element in elements:
            try:
                texte = nettoyer_texte(element.text)

                if (
                    element.is_displayed()
                    and len(texte) >= longueur_min
                ):
                    return texte

            except WebDriverException:
                pass

    return ""


def rubrique_depuis_url(url):
    partie = urlparse(url).path.strip("/").split("/")[0]

    correspondances = {
        "economie-france": "Économie",
        "politique-societe": "Politique",
        "monde": "Monde",
        "finance-marches": "Finance",
        "industrie-services": "Industrie",
        "tech-medias": "Tech",
        "idees-debats": "Idées et débats",
        "pme-regions": "PME et régions",
        "patrimoine": "Patrimoine",
        "weekend": "Week-end"
    }

    return correspondances.get(
        partie,
        partie.replace("-", " ").title()
    )


def extraire_chapeau(driver):
    chapeau = trouver_premier_texte(
        driver,
        [
            "main [class*='chapo']",
            "article [class*='chapo']",
            "main [class*='intro']",
            "article [class*='intro']",
            "main header p",
            "article header p"
        ],
        longueur_min=40
    )

    if chapeau:
        return chapeau[:300]

    
    paragraphes = driver.find_elements(
        By.CSS_SELECTOR,
        "main p, article p"
    )

    for paragraphe in paragraphes:
        texte = nettoyer_texte(paragraphe.text)

        if 60 <= len(texte) <= 600:
            return texte[:300]

    
    descriptions = driver.find_elements(
        By.CSS_SELECTOR,
        "meta[name='description']"
    )

    if descriptions:
        return nettoyer_texte(
            descriptions[0].get_attribute("content")
        )[:300]

    return "Non visible"


def extraire_heure(driver):
    elements_time = driver.find_elements(
        By.TAG_NAME,
        "time"
    )

    for element in elements_time:
        valeur = (
            nettoyer_texte(element.text)
            or nettoyer_texte(
                element.get_attribute("datetime")
            )
        )

        resultat = re.search(
            r"\b(?:[01]?\d|2[0-3])(?:h|:)[0-5]\d\b",
            valeur
        )

        if resultat:
            return resultat.group(0)

    texte_page = nettoyer_texte(
        driver.find_element(By.TAG_NAME, "body").text
    )

    resultat = re.search(
        r"(?:Publié|Mis à jour).*?"
        r"(\b(?:[01]?\d|2[0-3])(?:h|:)[0-5]\d\b)",
        texte_page,
        flags=re.IGNORECASE
    )

    if resultat:
        return resultat.group(1)

    return "Non visible"


def extraire_premium(driver, premium_une):
    texte_page = nettoyer_texte(
        driver.find_element(By.TAG_NAME, "body").text
    ).lower()

    elements_premium = driver.find_elements(
        By.CSS_SELECTOR,
        "[class*='premium'], "
        "[class*='abonne'], "
        "svg[class*='lock']"
    )

    return (
        premium_une
        or len(elements_premium) > 0
        or "réservé aux abonnés" in texte_page
        or "cet article est réservé" in texte_page
    )


def completer_article(driver, article, numero):
    try:
        driver.get(article["url"])

        titre = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.TAG_NAME, "h1")
            )
        ).text

        titre = nettoyer_titre(titre)

        if titre:
            article["titre"] = titre

        article["rubrique"] = rubrique_depuis_url(
            article["url"]
        )

        article["chapeau"] = extraire_chapeau(driver)
        article["heure_publi"] = extraire_heure(driver)

        article["premium"] = extraire_premium(
            driver,
            article["premium"]
        )

        print(
            f"{numero} - {article['titre'][:70]}"
        )

        return article

    except Exception as erreur:
        faire_capture(
            driver,
            f"lesechos_article_{numero}_erreur"
        )

        print(
            f"Article {numero} ignoré :",
            erreur
        )

        return None



tester_requests()

print("\nMesure du mode normal...")
temps_normal = mesurer_chargement(
    headless=False
)

print("Mesure du mode headless...")
temps_headless = mesurer_chargement(
    headless=True
)

if temps_normal is not None:
    print(
        f"Mode normal : "
        f"{temps_normal:.2f} seconde(s)"
    )

if temps_headless is not None:
    print(
        f"Mode headless : "
        f"{temps_headless:.2f} seconde(s)"
    )

if (
    temps_normal is not None
    and temps_headless is not None
    and temps_headless > 0
):
    gain = temps_normal / temps_headless

    print(
        f"Rapport normal/headless : {gain:.2f}"
    )


driver = creer_driver(headless=False)
resultats = []

try:
    driver.get(URL)
    accepter_cookies(driver)

    articles_une = recuperer_articles_une(driver)

    print(
        f"\n{len(articles_une)} article(s) "
        "seront visités."
    )

    for numero, article in enumerate(
        articles_une,
        start=1
    ):
        resultat = completer_article(
            driver,
            article,
            numero
        )

        if resultat is not None:
            resultats.append(resultat)

finally:
    try:
        driver.quit()
    except WebDriverException:
        pass



resultats_export = []

for article in resultats:
    resultats_export.append(
        {
            "titre": article["titre"],
            "rubrique": article["rubrique"],
            "chapeau": article["chapeau"],
            "heure_publi": article["heure_publi"],
            "premium": article["premium"]
        }
    )


with open(
    "lesechos.json",
    "w",
    encoding="utf-8"
) as fichier:
    json.dump(
        resultats_export,
        fichier,
        indent=2,
        ensure_ascii=False
    )


print(
    f"\n{len(resultats_export)} article(s) "
    "exporté(s) dans lesechos.json."
)