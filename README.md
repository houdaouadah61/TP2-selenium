TP Selenium - Doctolib et Les Echos

Présentation

Ce projet a été réalisé dans le cadre du module Web Scraping du Mastère Dev, Data & IA.

Deux sites ont été étudiés :

Doctolib

Les Echos

Installation

Créer un environnement virtuel puis installer les dépendances :

python -m venv .venv

Activation sous PowerShell :

.\.venv\Scripts\Activate.ps1

Installation :

pip install -r requirements.txt

Lancer les scripts

Scraper Doctolib :

python doctolib_scraper.py

Scraper Les Echos :

python lesechos_scraper.py

Comparer le mode normal et le mode headless :

python comparaison_headless.py

Résultats obtenus

Doctolib

Le script exporte 10 médecins dans doctolib.json.

Chaque médecin contient les champs suivants :

nom_specialite

adresse

type_consultation

prochains_creneaux

url_fiche

Certains médecins ne présentent pas de créneau visible au moment du test. Dans ce cas, la liste prochains_creneaux reste vide afin de ne pas inventer de donnée.

Les Echos

Le script exporte 15 articles dans lesechos.json.

Chaque article contient les champs suivants :

titre

rubrique

chapeau

heure_publi

premium


Comparaison du mode normal et du mode headless

Un test a été réalisé sur la page d'accueil du site Les Echos.

Mode

Temps

Mode normal

1,95 s

Mode headless

1,91 s

Le gain mesuré est de 1,02.

Le mode headless est donc légèrement plus rapide dans ce test, avec une différence de 0,04 seconde.

Le gain reste faible car il dépend notamment :

de la connexion Internet ;

du temps de réponse du site ;

des performances de l'ordinateur ;

Lorsqu'une erreur importante est détectée, une capture est enregistrée dans le dossier :

screenshots/

Le dossier contient notamment les captures des tests et des erreurs rencontrées pendant le développement.

Fichiers principaux

TP2/
├── doctolib_scraper.py
├── doctolib.json
├── lesechos_scraper.py
├── lesechos.json
├── comparaison_headless.py
├── comparaison_headless.json
├── defi1_cookies.py
├── defi1_resultat_final.json
├── defi2_antibot.py
├── defi2_resultats.json
├── defi3_robustesse.py
├── defi3_reference.json
├── defi3_resultat.json
├── requirements.txt
├── README.md
└── screenshots/

Défis réalisés

Défi 1 - Cookies

Les tests d'injection ont donné les résultats suivants :

sans cookie : bannière présente ;

didomi_token seul : bannière absente ;

euconsent-v2 seul : bannière présente ;

les deux cookies : bannière absente.

Le cookie didomi_token permet donc de reproduire le consentement sans cliquer sur la bannière.

Lors du test, un seul cookie appartenant à un domaine tiers a été détecté automatiquement. Aucun résultat supplémentaire n'a été inventé.

Défi 2 - Détection anti-bot

Résultats obtenus :

Mode

navigator.webdriver

Normal

true

Stealth

false

Headless

false

Le mode stealth masque la propriété navigator.webdriver.

l'automatisation.

Défi 3 - Robustesse des sélecteurs

Une première référence a été enregistrée dans defi3_reference.json.

Le script utilise plusieurs solutions de secours pour récupérer les informations lorsqu'un sélecteur principal ne fonctionne plus.

La seconde comparaison doit être réalisée trois jours après la première exécution en relançant :

python defi3_robustesse.py


## Pourquoi Selenium plutôt que requests ?

La bibliothèque requests récupère le HTML envoyé par le serveur, mais elle ne permet pas de gérer facilement les éléments chargés en JavaScript.

Selenium est utilisé dans ce TP car il permet de piloter un vrai navigateur, d'accepter les cookies, d'attendre les éléments dynamiques avec WebDriverWait, de faire défiler la page et de prendre des captures d'écran en cas d'erreur.
