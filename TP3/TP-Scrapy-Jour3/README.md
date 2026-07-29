# TP Scrapy - AlloCiné et Boursorama

## TP 1 - AlloCiné

Le spider AlloCiné récupère 50 films en suivant les liens vers les fiches
détaillées.

Pour chaque film, je récupère :

- le titre ;
- l'année ;
- le réalisateur ;
- la note presse ;
- la note spectateurs ;
- l'URL.

Les données sont nettoyées avec un pipeline puis enregistrées dans
`films.json` et `films.csv`.



## TP 2 - Boursorama

Le spider Boursorama récupère 25 actions du palmarès français.

Pour chaque action, je récupère :

- le libellé ;
- le cours ;
- la variation ;
- le volume ;
- le code ISIN.

Les données sont enregistrées dans la base SQLite `bourse.db`.

Le code ISIN est unique dans la base pour éviter les doublons.

## Défi 1 - Agenda local

l'agenda « Que faire à Paris ».
Le spider récupère le titre, la date et l'URL de 25 événements.
Certains liens apparaissaient plusieurs fois, donc j'ai supprimé les doublons.
Les dates étaient présentes dans le texte des pages et non dans une balise précise.
La structure était donc un peu moins simple que celle d'AlloCiné.

Les résultats sont enregistrés dans `evenements_paris.csv`.

## Défi 2 - Performances du crawl

J'ai testé plusieurs valeurs de `CONCURRENT_REQUESTS` sur 50 films.

| CONCURRENT_REQUESTS | Temps | Items par seconde |
|---:|---:|---:|
| 1 | 56,86 s | 0,88 |
| 4 | 56,89 s | 0,88 |
| 8 | 56,96 s | 0,88 |
| 16 | 56,99 s | 0,88 |

Les résultats sont presque identiques. Dans ce projet, le délai d'une seconde
entre les requêtes limite la vitesse du crawl. Augmenter la concurrence
n'améliore donc pas vraiment le temps total.

Avec AutoThrottle, le crawl a duré 68,68 secondes. Il était plus lent pendant
ce test, mais il permet d'adapter automatiquement la vitesse selon le temps de
réponse du serveur.

Le crawl a récupéré 50 films pour 56 réponses, soit un ratio d'environ 0,89.

## Défi 3 - Analyse Boursorama

Le script `analyse_bourse.py` permet de :

- afficher les cinq plus fortes hausses ;
- afficher les baisses lorsqu'elles existent ;
- afficher les volumes supérieurs à deux fois la moyenne ;
- exporter les données dans `analyse_bourse.csv`.

Pendant le dernier crawl, aucune baisse n'était présente.

ALTEN avait une hausse d'environ 19,84 %. Cette hausse peut être liée aux
résultats publiés par l'entreprise et à l'amélioration de ses prévisions.

Sopra Steria avait une hausse d'environ 13,07 %. Le groupe avait publié une
progression de son activité et relevé son objectif de croissance.

