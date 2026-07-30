import json
import sys
import time
from urllib.parse import quote_plus
import feedparser
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Etudiante-IPSSI-OSINT/1.0"
}


def chercher_entreprise(nom):
    

    url = "https://recherche-entreprises.api.gouv.fr/search"

    parametres = {
        "q": nom,
        "per_page": 1
    }

    try:
        reponse = requests.get(
            url,
            params=parametres,
            headers=HEADERS,
            timeout=20
        )

        reponse.raise_for_status()
        donnees = reponse.json()

        if not donnees.get("results"):
            return {
                "resultat": "Entreprise non trouvée"
            }

        entreprise = donnees["results"][0]
        siege = entreprise.get("siege") or {}

        activite = entreprise.get("activite_principale")

        if activite is None:
            activite = siege.get("activite_principale")

        date_creation = entreprise.get("date_creation")

        if date_creation is None:
            date_creation = siege.get("date_creation")

        effectif = entreprise.get(
            "tranche_effectif_salarie"
        )

        if effectif is None:
            effectif = siege.get(
                "tranche_effectif_salarie"
            )

        return {
            "siren": entreprise.get("siren"),
            "nom_complet": entreprise.get("nom_complet"),
            "adresse_siege": siege.get("adresse"),
            "activite_principale": activite,
            "date_creation": date_creation,
            "tranche_effectif": effectif
        }

    except requests.exceptions.ConnectionError:
        return {
            "erreur": "Connexion impossible avec l'API."
        }

    except requests.exceptions.Timeout:
        return {
            "erreur": "L'API a mis trop de temps à répondre."
        }

    except requests.RequestException as erreur:
        return {
            "erreur": str(erreur)
        }

    except ValueError:
        return {
            "erreur": "La réponse n'est pas un JSON valide."
        }


def scraper_wikipedia(nom_page):
    

    nom_page = nom_page.replace(" ", "_")

    url = (
        "https://fr.wikipedia.org/wiki/"
        + nom_page
    )

    try:
        reponse = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        reponse.raise_for_status()

        soup = BeautifulSoup(
            reponse.text,
            "lxml"
        )

        infobox = {}

        table = soup.select_one(
            "table.infobox_v3, table.infobox"
        )

        if table:
            lignes = table.select("tr")

            for ligne in lignes:
                cellule_cle = ligne.select_one("th")
                cellule_valeur = ligne.select_one("td")

                if cellule_cle and cellule_valeur:
                    cle = cellule_cle.get_text(
                        " ",
                        strip=True
                    )

                    valeur = cellule_valeur.get_text(
                        " ",
                        strip=True
                    )

                    infobox[cle] = valeur[:200]

        introduction = ""

        paragraphes = soup.find_all("p")

        for paragraphe in paragraphes:

            
            if paragraphe.find_parent("table") is not None:
                continue

            texte = paragraphe.get_text(
                " ",
                strip=True
            )

            if (
                len(texte) > 80
                and "TotalEnergies" in texte
            ):
                introduction = texte[:500]
                break

        return {
            "url": url,
            "introduction": introduction,
            "infobox": infobox
        }

    except requests.exceptions.ConnectionError:
        return {
            "erreur": "Connexion impossible avec Wikipédia."
        }

    except requests.exceptions.Timeout:
        return {
            "erreur": (
                "Wikipédia a mis trop de temps à répondre."
            )
        }

    except requests.RequestException as erreur:
        return {
            "erreur": str(erreur)
        }


def chercher_articles(nom, nombre_max=10):
    

    recherche = quote_plus(nom)

    url = (
        "https://news.google.com/rss/search?q="
        + recherche
        + "&hl=fr&gl=FR&ceid=FR:fr"
    )

    try:
        reponse = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        reponse.raise_for_status()

        flux = feedparser.parse(
            reponse.content
        )

        articles = []

        for article in flux.entries[:nombre_max]:

            source = article.get("source", {})

            if source:
                nom_source = source.get("title", "")
            else:
                nom_source = ""

            articles.append(
                {
                    "titre": article.get(
                        "title",
                        ""
                    ),
                    "source": nom_source,
                    "date": article.get(
                        "published",
                        ""
                    ),
                    "lien": article.get(
                        "link",
                        ""
                    )
                }
            )

        return articles

    except requests.exceptions.ConnectionError:
        return [
            {
                "erreur": (
                    "Connexion impossible avec Google News."
                )
            }
        ]

    except requests.exceptions.Timeout:
        return [
            {
                "erreur": (
                    "Google News a mis trop de temps à répondre."
                )
            }
        ]

    except requests.RequestException as erreur:
        return [
            {
                "erreur": str(erreur)
            }
        ]


def construire_fiche(nom_entreprise):
    """Regroupe les résultats des trois sources."""

    fiche = {
        "entite": nom_entreprise
    }

    print("Recherche dans l'Annuaire des Entreprises...")

    fiche["entreprise"] = chercher_entreprise(
        nom_entreprise
    )

    time.sleep(1)

    print("Recherche sur Wikipédia...")

    fiche["wikipedia"] = scraper_wikipedia(
        "TotalEnergies"
    )

    time.sleep(1)

    print("Recherche dans la presse...")

    fiche["presse"] = chercher_articles(
        "TotalEnergies",
        10
    )

    fiche["nombre_articles"] = len(
        fiche["presse"]
    )

    return fiche


if __name__ == "__main__":

    if len(sys.argv) > 1:
        nom_entreprise = " ".join(sys.argv[1:])
    else:
        nom_entreprise = "TOTALENERGIES SE"

    print(
        "Construction de la fiche :",
        nom_entreprise
    )

    fiche = construire_fiche(
        nom_entreprise
    )

    with open(
        "fiche_entite.json",
        "w",
        encoding="utf-8"
    ) as fichier:

        json.dump(
            fiche,
            fichier,
            indent=4,
            ensure_ascii=False
        )

    print("\nFiche terminée.")

    print(
        "SIREN :",
        fiche["entreprise"].get(
            "siren",
            "Non trouvé"
        )
    )

    print(
        "Nombre d'articles :",
        fiche["nombre_articles"]
    )

    print(
        "Fichier créé : fiche_entite.json"
    )