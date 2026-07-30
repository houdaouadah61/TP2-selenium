TP OSINT - Web Scraping

Organisation du projet

TP_OSINT/
├── td41_domaine.py
├── rapport_domaine.json
├── td42_entite.py
├── fiche_entite.json
├── ETHIQUE.md
├── README.md
├── requirements.txt
└── veille/
    ├── scrapy.cfg
    ├── analyser_db.py
    ├── defi1_analyse.py
    ├── mentions.csv
    ├── veille.db
    └── veille/
        ├── items.py
        ├── pipelines.py
        ├── settings.py
        └── spiders/
            └── rss_spider.py

Installation

Créer l’environnement virtuel :

python -m venv venv

Activer l’environnement :

.env\Scripts\Activate.ps1

Installer les bibliothèques :

python -m pip install -r requirements.txt

TD 4.1 - Analyse d’un domaine

Le script récupère :

l’adresse IP ;

le WHOIS ;

les headers HTTP ;

les sous-domaines avec crt.sh ;

le fichier robots.txt.

Commande utilisée :

python td41_domaine.py ipssi.fr

Résultat :

rapport_domaine.json

Pendant mon test, crt.sh ne répondait pas correctement.Le fichier contient donc zéro sous-domaine, mais cela ne veut pas dire qu’il n’existe aucun sous-domaine.

TD 4.2 - Analyse d’une entreprise
Le script utilise :

l’API officielle de recherche des entreprises ;

Wikipédia ;

des articles de presse avec un flux RSS.

Commande utilisée :

python td42_entite.py "TOTALENERGIES SE"

Résultat :

fiche_entite.json

Le script a trouvé le SIREN de l’entreprise et plusieurs articles de presse.

TD 4.3 - Veille RSS avec Scrapy

Le spider regarde plusieurs flux RSS et cherche les articles qui contiennent le mot-clé choisi.

Pour lancer le spider :

cd veille
scrapy check
scrapy crawl rss_spider -L INFO

Pour voir les résultats dans la base :

python analyser_db.py

Résultats créés :

mentions.csv
veille.db

Après avoir modifié les mots-clés du score, le spider a enregistré 12 articles :

3 articles neutres ;

8 articles négatifs ;

1 article positif.

Score des articles

Le score utilisé est simple :

0 = neutre
1 = négatif
2 = positif

