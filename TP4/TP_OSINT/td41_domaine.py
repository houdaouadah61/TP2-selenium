import json
import socket
import sys
import time
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
import requests
import urllib3
import whois

CONTACT_EMAIL = "ton.adresse@ipssi.fr"

USER_AGENT = (
    f"Houda-IPSSI-OSINT/1.0 "
    f"(projet pédagogique ; contact: {CONTACT_EMAIL})"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,*/*;q=0.8"
    ),
}

FICHIER_SORTIE = Path("rapport_domaine.json")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def normaliser_domaine(valeur):
    
    valeur = valeur.strip()

    if "://" not in valeur:
        valeur = "https://" + valeur

    domaine = urlparse(valeur).netloc
    domaine = domaine.split("@")[-1]
    domaine = domaine.split(":")[0]
    domaine = domaine.strip().lower()

    if not domaine:
        raise ValueError("Nom de domaine invalide.")

    return domaine


def convertir_json(objet):
    
    if isinstance(objet, (datetime, date)):
        return objet.isoformat()

    if isinstance(objet, set):
        return sorted(objet)

    if isinstance(objet, bytes):
        return objet.decode("utf-8", errors="replace")

    return str(objet)


def transformer_en_liste(valeur):
    
    if valeur is None:
        return []

    if isinstance(valeur, (list, tuple, set)):
        return list(valeur)

    return [valeur]


def recuperer_adresses_ip(domaine):
    
    try:
        informations = socket.gethostbyname_ex(domaine)
        adresses = sorted(set(informations[2]))

        return {
            "adresse_ip": adresses[0] if adresses else None,
            "adresses_ip": adresses,
            "erreur": None,
        }

    except socket.gaierror as erreur:
        return {
            "adresse_ip": None,
            "adresses_ip": [],
            "erreur": str(erreur),
        }


def recuperer_whois(domaine):
    
    try:
        resultat = whois.whois(domaine)

        return {
            "nom_domaine": transformer_en_liste(
                resultat.get("domain_name")
            ),
            "registrar": resultat.get("registrar"),
            "serveur_whois": resultat.get("whois_server"),
            "date_creation": transformer_en_liste(
                resultat.get("creation_date")
            ),
            "date_expiration": transformer_en_liste(
                resultat.get("expiration_date")
            ),
            "date_mise_a_jour": transformer_en_liste(
                resultat.get("updated_date")
            ),
            "serveurs_dns": transformer_en_liste(
                resultat.get("name_servers")
            ),
            "statuts": transformer_en_liste(
                resultat.get("status")
            ),
            "pays": resultat.get("country"),
            "emails": transformer_en_liste(
                resultat.get("emails")
            ),
            "erreur": None,
        }

    except Exception as erreur:
        return {
            "nom_domaine": [],
            "registrar": None,
            "serveur_whois": None,
            "date_creation": [],
            "date_expiration": [],
            "date_mise_a_jour": [],
            "serveurs_dns": [],
            "statuts": [],
            "pays": None,
            "emails": [],
            "erreur": str(erreur),
        }



def effectuer_requete(url, timeout=15):
    
    try:
        reponse = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
            verify=True,
        )

        return reponse, {
            "verification_ssl": True,
            "avertissement_ssl": None,
        }

    except requests.exceptions.SSLError as erreur_ssl:
        print(
            f"Erreur de certificat SSL pour {url}. "
            "Nouvelle tentative sans validation SSL..."
        )

        reponse = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
            verify=False,
        )

        return reponse, {
            "verification_ssl": False,
            "avertissement_ssl": (
                "La validation du certificat SSL a échoué. "
                "La requête a été répétée avec verify=False. "
                f"Détail : {erreur_ssl}"
            ),
        }



def recuperer_headers_http(domaine):
    
    url = f"https://{domaine}/"

    try:
        reponse, informations_ssl = effectuer_requete(url)

        headers = dict(reponse.headers)
        headers_minuscules = {
            cle.lower(): valeur
            for cle, valeur in headers.items()
        }

        return {
            "url_demandee": url,
            "url_finale": reponse.url,
            "code_http": reponse.status_code,
            "headers": headers,
            "serveur": headers_minuscules.get(
                "server",
                "non indiqué",
            ),
            "hsts_present": (
                "strict-transport-security" in headers_minuscules
            ),
            "csp_presente": (
                "content-security-policy" in headers_minuscules
            ),
            "verification_ssl": informations_ssl[
                "verification_ssl"
            ],
            "avertissement_ssl": informations_ssl[
                "avertissement_ssl"
            ],
            "erreur": None,
        }

    except requests.RequestException as erreur:
        return {
            "url_demandee": url,
            "url_finale": None,
            "code_http": None,
            "headers": {},
            "serveur": "non récupéré",
            "hsts_present": False,
            "csp_presente": False,
            "verification_ssl": None,
            "avertissement_ssl": None,
            "erreur": str(erreur),
        }



def recuperer_sous_domaines(domaine):
    
    url = "https://crt.sh/"
    parametres = {
        "q": f"%.{domaine}",
        "output": "json",
    }

    for tentative in range(1, 3):
        try:
            reponse = requests.get(
                url,
                params=parametres,
                headers=HEADERS,
                timeout=30,
            )

            reponse.raise_for_status()
            donnees = reponse.json()

            sous_domaines = set()

            for certificat in donnees:
                noms = certificat.get("name_value", "")

                for nom in noms.splitlines():
                    nom = nom.strip().lower()
                    nom = nom.removeprefix("*.")

                    if (
                        nom == domaine
                        or nom.endswith("." + domaine)
                    ):
                        sous_domaines.add(nom)

            return sorted(sous_domaines)

        except (
            requests.RequestException,
            ValueError,
        ) as erreur:
            print(
                f"Erreur crt.sh, tentative {tentative} : "
                f"{erreur}"
            )

            if tentative < 2:
                print("Nouvelle tentative dans 3 secondes...")
                time.sleep(3)

    print(
        "crt.sh est indisponible. "
        "Aucun sous-domaine enregistré."
    )

    return []


def recuperer_robots_txt(domaine):
    
    url = f"https://{domaine}/robots.txt"

    try:
        reponse, informations_ssl = effectuer_requete(url)
        reponse.raise_for_status()

        
        contenu = reponse.text[:10000]

        return {
            "url": reponse.url,
            "code_http": reponse.status_code,
            "accessible": True,
            "contenu": contenu,
            "verification_ssl": informations_ssl[
                "verification_ssl"
            ],
            "avertissement_ssl": informations_ssl[
                "avertissement_ssl"
            ],
            "erreur": None,
        }

    except requests.RequestException as erreur:
        return {
            "url": url,
            "code_http": None,
            "accessible": False,
            "contenu": "",
            "verification_ssl": None,
            "avertissement_ssl": None,
            "erreur": str(erreur),
        }


def analyser_domaine(domaine):
    
    print(f"Analyse du domaine : {domaine}")

    dns = recuperer_adresses_ip(domaine)

    
    time.sleep(1)

    informations_whois = recuperer_whois(domaine)

    time.sleep(1)

    headers_http = recuperer_headers_http(domaine)

    time.sleep(1)

    print("Recherche des sous-domaines en cours...")
    sous_domaines = recuperer_sous_domaines(domaine)

    time.sleep(1)

    print("Lecture du fichier robots.txt...")
    robots_txt = recuperer_robots_txt(domaine)

    rapport = {
        "domaine": domaine,
        "date_analyse": datetime.now().astimezone().isoformat(),
        "user_agent": USER_AGENT,
        "adresse_ip": dns["adresse_ip"],
        "adresses_ip": dns["adresses_ip"],
        "erreur_dns": dns["erreur"],
        "whois": informations_whois,
        "headers_http": headers_http,
        "sous_domaines": sous_domaines,
        "nombre_sous_domaines": len(sous_domaines),
        "robots_txt": robots_txt,
        "limites": [
            (
                "Les données WHOIS peuvent être incomplètes ou "
                "masquées pour protéger les données personnelles."
            ),
            (
                "Les journaux crt.sh peuvent être temporairement "
                "indisponibles et ne recensent pas nécessairement "
                "tous les sous-domaines."
            ),
            (
                "Une requête effectuée sans validation SSL ne permet "
                "pas de vérifier avec certitude l'identité du serveur."
            ),
        ],
    }

    return rapport


def enregistrer_rapport(rapport):

    
    with FICHIER_SORTIE.open(
        "w",
        encoding="utf-8",
    ) as fichier:
        json.dump(
            rapport,
            fichier,
            ensure_ascii=False,
            indent=4,
            default=convertir_json,
        )

def main():
    if len(sys.argv) != 2:
        print(
            "Utilisation : python td41_domaine.py "
            "nom-du-domaine.fr"
        )
        sys.exit(1)

    try:
        domaine = normaliser_domaine(sys.argv[1])
        rapport = analyser_domaine(domaine)
        enregistrer_rapport(rapport)

        print("\nAnalyse terminée.")
        print(f"Adresse IP : {rapport['adresse_ip']}")
        print(
            "Nombre de sous-domaines : "
            f"{rapport['nombre_sous_domaines']}"
        )
        print(
            "Vérification SSL des headers : "
            f"{rapport['headers_http']['verification_ssl']}"
        )
        print(f"Fichier créé : {FICHIER_SORTIE}")

    except KeyboardInterrupt:
        print("\nAnalyse interrompue par l'utilisateur.")
        sys.exit(1)

    except Exception as erreur:
        print(f"Erreur inattendue : {erreur}")
        sys.exit(1)


if __name__ == "__main__":
    main()