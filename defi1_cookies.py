import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL_DOCTOLIB = "https://www.doctolib.fr/medecin-generaliste/montpellier"
FICHIER_DOCTOLIB = "cookies_doctolib.json"
FICHIER_MAIIA = "cookies_maiia.json"

os.makedirs("screenshots", exist_ok=True)


def creer_driver():
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    return driver


def attendre_page(driver):
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


def banniere_presente(driver, attente=6):
    
    xpath = (
        "//button[contains(., 'Tout accepter') "
        "or contains(., 'Accepter')]"
    )

    try:
        WebDriverWait(driver, attente).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        return True

    except TimeoutException:
        return False


def accepter_cookies(driver):
    xpath = (
        "//button[contains(., 'Tout accepter') "
        "or contains(., 'Accepter')]"
    )

    try:
        bouton = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        bouton.click()
        print("Cookies acceptés.")
        return True

    except TimeoutException:
        print("Bannière non trouvée.")
        return False


def charger_cookies(fichier):
    with open(fichier, "r", encoding="utf-8") as flux:
        contenu = json.load(flux)

    return contenu.get("apres_acceptation", [])


def chercher_cookie(cookies, nom):
    for cookie in cookies:
        if cookie.get("name") == nom:
            return cookie

    return None


def preparer_cookie(cookie):
    
    champs_acceptes = {
        "name",
        "value",
        "path",
        "domain",
        "secure",
        "httpOnly",
        "expiry",
        "sameSite",
    }

    resultat = {
        cle: valeur
        for cle, valeur in cookie.items()
        if cle in champs_acceptes
    }

    if "expiry" in resultat:
        resultat["expiry"] = int(resultat["expiry"])

    return resultat


def nettoyer_navigateur(driver):
    
    driver.delete_all_cookies()

    try:
        driver.execute_script(
            "window.localStorage.clear();"
            "window.sessionStorage.clear();"
        )
    except WebDriverException:
        pass


def tester_injection(nom_test, cookies_a_injecter):
    
    driver = creer_driver()

    try:
        driver.get(URL_DOCTOLIB)
        attendre_page(driver)
        nettoyer_navigateur(driver)

        for cookie in cookies_a_injecter:
            driver.add_cookie(preparer_cookie(cookie))

        driver.get(URL_DOCTOLIB)
        attendre_page(driver)

        presente = banniere_presente(driver)

        driver.save_screenshot(
            f"screenshots/injection_{nom_test}.png"
        )

        print(
            f"{nom_test} : bannière "
            f"{'présente' if presente else 'absente'}"
        )

        return {
            "test": nom_test,
            "cookies_injectes": [
                cookie["name"]
                for cookie in cookies_a_injecter
            ],
            "banniere_presente": presente,
        }

    finally:
        try:
            driver.quit()
        except WebDriverException:
            pass


def recuperer_tous_les_cookies(driver):
    
    try:
        resultat = driver.execute_cdp_cmd(
            "Storage.getCookies",
            {}
        )
        return resultat.get("cookies", [])

    except WebDriverException:
        resultat = driver.execute_cdp_cmd(
            "Network.getAllCookies",
            {}
        )
        return resultat.get("cookies", [])


def trouver_cookies_tiers_doctolib():
    driver = creer_driver()

    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.get(URL_DOCTOLIB)
        attendre_page(driver)
        accepter_cookies(driver)

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        
        try:
            WebDriverWait(driver, 8).until(
                lambda navigateur: len(
                    recuperer_tous_les_cookies(navigateur)
                ) >= 1
            )
        except TimeoutException:
            pass

        tous = recuperer_tous_les_cookies(driver)

        tiers = []

        for cookie in tous:
            domaine = cookie.get("domain", "").lstrip(".")

            if domaine and not domaine.endswith("doctolib.fr"):
                tiers.append(cookie)

        return tiers

    finally:
        try:
            driver.quit()
        except WebDriverException:
            pass


def valeur_encodee(valeur):
    valeur = str(valeur or "")

    if len(valeur) > 30:
        return "Oui"

    if re.search(r"[%+/=_~.-]", valeur):
        return "Oui"

    return "Non"


def duree_cookie(cookie):
    expiration = cookie.get("expiry")

    if not expiration:
        return "Session"

    secondes = float(expiration) - datetime.now(
        timezone.utc
    ).timestamp()

    if secondes <= 0:
        return "Expiré"

    minutes = secondes / 60
    heures = minutes / 60
    jours = heures / 24

    if jours >= 2:
        return f"{jours:.0f} jours"

    if heures >= 2:
        return f"{heures:.0f} heures"

    return f"{minutes:.0f} minutes"


def cookies_nouveaux(fichier):
    
    with open(fichier, "r", encoding="utf-8") as flux:
        contenu = json.load(flux)

    avant = contenu.get("avant_acceptation", [])
    apres = contenu.get("apres_acceptation", [])

    noms_avant = {
        cookie.get("name")
        for cookie in avant
    }

    return [
        cookie
        for cookie in apres
        if cookie.get("name") not in noms_avant
    ]


def cookie_par_nom(cookies, nom):
    for cookie in cookies:
        if cookie.get("name") == nom:
            return cookie

    return None


def conclusion_injection(resultats):
    baseline = next(
        resultat
        for resultat in resultats
        if resultat["test"] == "sans_cookie"
    )

    if not baseline["banniere_presente"]:
        return (
            "Test non concluant : la bannière était déjà absente "
            "sans injection."
        )

    ordre = [
        "didomi_token_seul",
        "euconsent_v2_seul",
        "deux_cookies",
    ]

    for nom_test in ordre:
        resultat = next(
            resultat
            for resultat in resultats
            if resultat["test"] == nom_test
        )

        if not resultat["banniere_presente"]:
            noms = ", ".join(resultat["cookies_injectes"])

            return (
                "Le premier scénario qui masque la bannière est : "
                f"{noms}."
            )

    return (
        "Aucun des trois scénarios n'a suffi à masquer "
        "la bannière. Un stockage local ou un autre cookie "
        "est probablement aussi nécessaire."
    )


def creer_rapport(
    resultats_injection,
    cookies_tiers,
    services_tiers,
):
    lignes = [
        "# Défi 1 - Cookie forensics",
        "",
        "## Test d'injection du consentement Doctolib",
        "",
        "| Test | Cookies injectés | Bannière présente |",
        "|---|---|---|",
    ]

    for resultat in resultats_injection:
        noms = ", ".join(
            resultat["cookies_injectes"]
        ) or "Aucun"

        banniere = (
            "Oui"
            if resultat["banniere_presente"]
            else "Non"
        )

        lignes.append(
            f"| {resultat['test']} | {noms} | {banniere} |"
        )

    lignes.extend(
        [
            "",
            conclusion_injection(resultats_injection),
            "",
            "Les valeurs complètes des cookies ne sont pas "
            "recopiées dans le rapport.",
            "",
            "## Cookies de domaines tiers détectés",
            "",
        ]
    )

    if cookies_tiers:
        lignes.extend(
            [
                "| Nom | Domaine | Durée | Valeur encodée |",
                "|---|---|---|---|",
            ]
        )

        for cookie in cookies_tiers[:10]:
            lignes.append(
                "| "
                f"{cookie.get('name', '')} | "
                f"{cookie.get('domain', '')} | "
                f"{duree_cookie(cookie)} | "
                f"{valeur_encodee(cookie.get('value'))} |"
            )
    else:
        lignes.extend(
            [
                "Aucun cookie appartenant à un domaine externe "
                "à `doctolib.fr` n'a été exposé par Chrome.",
                "",
                "Le navigateur peut bloquer les cookies tiers ou "
                "les services externes peuvent déposer leurs cookies "
                "sur le domaine du site.",
            ]
        )

    lignes.extend(
        [
            "",
            "## Cookies liés à des services externes",
            "",
            "Ces cookies sont déposés sur les domaines des sites, "
            "mais leur fonction est assurée par un service externe.",
            "",
            "| Nom | Site observé | Domaine | Durée | Valeur encodée |",
            "|---|---|---|---|---|",
        ]
    )

    for nom_site, cookie in services_tiers:
        if cookie is None:
            continue

        lignes.append(
            "| "
            f"{cookie.get('name', '')} | "
            f"{nom_site} | "
            f"{cookie.get('domain', '')} | "
            f"{duree_cookie(cookie)} | "
            f"{valeur_encodee(cookie.get('value'))} |"
        )

    lignes.extend(
        [
            "",
            "## Comparaison Doctolib / Maiia",
            "",
            "- Doctolib utilise `didomi_token` et "
            "`euconsent-v2` pour le consentement.",
            "- Les mêmes noms n'ont pas été trouvés sur Maiia.",
            "- Maiia a notamment créé des cookies liés à la "
            "sécurité et à la mesure technique.",
            "",
            "## Limite",
            "",
            "`driver.get_cookies()` ne retourne que les cookies du "
            "domaine courant. Le script utilise donc aussi le "
            "protocole DevTools de Chrome pour rechercher les cookies "
            "du profil complet.",
        ]
    )

    Path("DEFIS_DEFI1.md").write_text(
        "\n".join(lignes),
        encoding="utf-8"
    )


if not os.path.exists(FICHIER_DOCTOLIB):
    raise FileNotFoundError(
        "Le fichier cookies_doctolib.json est introuvable."
    )

cookies_doctolib = charger_cookies(
    FICHIER_DOCTOLIB
)

didomi = chercher_cookie(
    cookies_doctolib,
    "didomi_token"
)

euconsent = chercher_cookie(
    cookies_doctolib,
    "euconsent-v2"
)

if didomi is None or euconsent is None:
    raise RuntimeError(
        "didomi_token ou euconsent-v2 manque dans "
        "cookies_doctolib.json."
    )


print("\n--- Tests d'injection ---")

resultats_injection = [
    tester_injection(
        "sans_cookie",
        []
    ),
    tester_injection(
        "didomi_token_seul",
        [didomi]
    ),
    tester_injection(
        "euconsent_v2_seul",
        [euconsent]
    ),
    tester_injection(
        "deux_cookies",
        [didomi, euconsent]
    ),
]


print("\n--- Recherche des cookies tiers ---")

cookies_tiers = trouver_cookies_tiers_doctolib()

print(
    len(cookies_tiers),
    "cookie(s) de domaines tiers détecté(s)."
)


nouveaux_doctolib = cookies_nouveaux(
    FICHIER_DOCTOLIB
)

nouveaux_maiia = []

if os.path.exists(FICHIER_MAIIA):
    nouveaux_maiia = cookies_nouveaux(
        FICHIER_MAIIA
    )


services_tiers = [
    (
        "Doctolib",
        cookie_par_nom(
            cookies_doctolib,
            "__cf_bm"
        )
    ),
    (
        "Maiia",
        cookie_par_nom(
            nouveaux_maiia,
            "datadome"
        )
    ),
    (
        "Maiia",
        cookie_par_nom(
            nouveaux_maiia,
            "dtCookie"
        )
    ),
]


resultat_final = {
    "tests_injection": resultats_injection,
    "conclusion_injection": conclusion_injection(
        resultats_injection
    ),
    "cookies_domaines_tiers": [
        {
            "name": cookie.get("name"),
            "domain": cookie.get("domain"),
            "duree": duree_cookie(cookie),
            "valeur_encodee": valeur_encodee(
                cookie.get("value")
            ),
        }
        for cookie in cookies_tiers
    ],
}


with open(
    "defi1_resultat_final.json",
    "w",
    encoding="utf-8"
) as fichier:
    json.dump(
        resultat_final,
        fichier,
        indent=2,
        ensure_ascii=False
    )


creer_rapport(
    resultats_injection,
    cookies_tiers,
    services_tiers,
)


print("\nDéfi 1 terminé.")
print("Fichiers créés :")
print("- defi1_resultat_final.json")
print("- DEFIS_DEFI1.md")
print("- screenshots/injection_*.png")
import time


def recuperer_cookies_json(donnees):
    

    cookies = []

    if isinstance(donnees, list):

        for element in donnees:
            cookies.extend(
                recuperer_cookies_json(element)
            )

    elif isinstance(donnees, dict):

        if "name" in donnees and "domain" in donnees:
            cookies.append(donnees)

        else:
            for valeur in donnees.values():
                cookies.extend(
                    recuperer_cookies_json(valeur)
                )

    return cookies


def lire_cookies(nom_fichier):
    

    if not os.path.exists(nom_fichier):
        return []

    with open(
        nom_fichier,
        "r",
        encoding="utf-8"
    ) as fichier:
        donnees = json.load(fichier)

    return recuperer_cookies_json(donnees)


def calculer_duree(cookie):
    

    expiration = (
        cookie.get("expiry")
        or cookie.get("expires")
    )

    if not expiration:
        return "Session"

    secondes = expiration - time.time()

    if secondes <= 0:
        return "Expiré"

    jours = secondes / 86400

    if jours >= 1:
        return f"Environ {jours:.0f} jour(s)"

    heures = secondes / 3600

    return f"Environ {heures:.0f} heure(s)"


def valeur_probablement_encodee(valeur):
    

    if not valeur:
        return False

    caracteres_speciaux = [
        "%",
        "=",
        "_",
        "-",
        "."
    ]

    return (
        len(valeur) > 40
        or any(
            caractere in valeur
            for caractere in caracteres_speciaux
        )
    )


cookies = []

cookies.extend(
    lire_cookies("cookies_doctolib.json")
)

cookies.extend(
    lire_cookies("cookies_maiia.json")
)



prestataires = {
    "__cf_bm": "Cloudflare",
    "datadome": "DataDome",
    "dtCookie": "Dynatrace",
    "rxVisitor": "Dynatrace",
    "didomi_token": "Didomi",
    "euconsent-v2": "Didomi / IAB"
}



ordre_priorite = [
    "__cf_bm",
    "datadome",
    "dtCookie",
    "didomi_token",
    "euconsent-v2",
    "rxVisitor"
]


cookies_uniques = {}

for cookie in cookies:
    nom = cookie.get("name", "")
    domaine = cookie.get("domain", "")

    cle = (nom, domaine)

    if cle not in cookies_uniques:
        cookies_uniques[cle] = cookie


selection = []

for nom_recherche in ordre_priorite:

    for cookie in cookies_uniques.values():

        if cookie.get("name") == nom_recherche:

            selection.append(
                {
                    "nom": cookie.get("name"),
                    "prestataire": prestataires.get(
                        cookie.get("name"),
                        "Non identifié"
                    ),
                    "domaine": cookie.get(
                        "domain",
                        "inconnu"
                    ),
                    "duree_de_vie": calculer_duree(
                        cookie
                    ),
                    "valeur_encodee_probable":
                        valeur_probablement_encodee(
                            cookie.get("value", "")
                        )
                }
            )

            break

    if len(selection) == 3:
        break


print("\n--- Trois cookies à analyser ---")

for numero, cookie in enumerate(
    selection,
    start=1
):
    print(
        f"{numero}. {cookie['nom']} "
        f"- {cookie['prestataire']} "
        f"- {cookie['domaine']}"
    )


if len(selection) < 3:
    print(
        "Attention : moins de trois cookies "
        "correspondants ont été observés."
    )



resultat_final = {}

if os.path.exists("defi1_resultat_final.json"):

    with open(
        "defi1_resultat_final.json",
        "r",
        encoding="utf-8"
    ) as fichier:
        resultat_final = json.load(fichier)


resultat_final[
    "trois_cookies_a_analyser"
] = selection


with open(
    "defi1_resultat_final.json",
    "w",
    encoding="utf-8"
) as fichier:
    json.dump(
        resultat_final,
        fichier,
        indent=2,
        ensure_ascii=False
    )


print(
    "\nLes trois cookies ont été ajoutés dans "
    "defi1_resultat_final.json."
)