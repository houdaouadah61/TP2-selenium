# TP Scrapy — AlloCiné, Boursorama et défis

## Présentation

Ce projet contient deux TP obligatoires et trois défis réalisés avec Scrapy.

## TP 1 — AlloCiné

Le spider AlloCiné récupère 50 films en suivant les liens entre les pages
de classement et les fiches détaillées.

Champs récupérés :

- titre ;
- année ;
- réalisateur ;
- note presse ;
- note spectateurs ;
- URL.

Les données sont nettoyées avec un CleanPipeline puis exportées dans :

- films.json ;
- films.csv.

Le projet utilise robots.txt, un délai d'une seconde, AutoThrottle et
trois tentatives en cas d'erreur HTTP.

## TP 2 — Boursorama

Le spider Boursorama récupère 25 actions du palmarès français.

Champs récupérés :

- libellé ;
- cours ;
- variation ;
- volume ;
- code ISIN.

Les données sont enregistrées dans la base SQLite bourse.db.

La colonne isin possède une contrainte UNIQUE pour empêcher les doublons.
Les 25 codes ISIN collectés ont été contrôlés et sont valides.

## Défi 1 — Agenda local parisien

J'ai choisi l'agenda « Que faire à Paris » de la Ville de Paris.

Contrairement à AlloCiné, plusieurs liens vers le même événement apparaissent
sur la page, ce qui oblige à supprimer les doublons. Les dates ne sont pas
placées dans une balise HTML spécifique et doivent être recherchées dans le
texte de la fiche. La structure est donc un peu moins prévisible qu'AlloCiné,
mais les pages conservent un titre, une date et une URL exploitables.

Le spider a récupéré 25 événements dans evenements_paris.csv.

## Défi 2 — Performances du crawl AlloCiné

Les tests ont été réalisés sur 50 films.

| CONCURRENT_REQUESTS | Temps | Items par seconde |
|---:|---:|---:|
| 1 | 56,86 s | 0,88 |
| 4 | 56,89 s | 0,88 |
| 8 | 56,96 s | 0,88 |
| 16 | 56,99 s | 0,88 |

L'augmentation du nombre de requêtes simultanées n'a pas amélioré les
performances. Les quatre crawls restent proches de 57 secondes.

Le principal facteur limitant est DOWNLOAD_DELAY = 1. Scrapy espace les
requêtes envoyées au domaine AlloCiné. Augmenter CONCURRENT_REQUESTS ne crée
donc pas de parallélisme supplémentaire utile dans cette configuration.

Le test avec AutoThrottle a duré 68,68 secondes. Il a récupéré 50 films pour
56 réponses reçues, soit un ratio items/réponses proche de 0,89.

AutoThrottle est plus lent sur ce petit crawl, car il adapte progressivement
le rythme des requêtes. Il reste utile sur un crawl plus long ou lorsque le
temps de réponse du serveur varie.

Un ratio inférieur à 0,5 signifierait que plus de la moitié des réponses ne
produisent aucun item. Cela pourrait révéler des erreurs HTTP, des pages
inutiles ou des sélecteurs devenus incorrects.

## Défi 3 — SQL et interprétation financière

Le script analyse_bourse.py réalise les traitements suivants :

- classement des cinq principales hausses ;
- classement des baisses lorsqu'elles existent ;
- détection des volumes supérieurs à deux fois la moyenne ;
- export des actions dans analyse_bourse.csv.

Lors du dernier crawl, aucune variation négative n'était présente dans les
25 actions collectées.

### Analyse de deux hausses

Coller ici l'analyse déjà réalisée pour les deux entreprises sélectionnées,
avec le nom de chaque source d'actualité et la date de consultation.

## Fichiers principaux

- films.json
- films.csv
- boursorama/bourse.db
- boursorama/analyse_bourse.py
- boursorama/analyse_bourse.csv
- defi_local/evenements_paris.csv
- performance_allocine.csv