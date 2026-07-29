# TP Scrapy — AlloCiné, Boursorama et défis

## Présentation

Ce projet contient deux spiders principaux et trois défis réalisés avec Scrapy.

## TP 1 — AlloCiné

Le spider AlloCiné récupère 50 films en suivant les liens entre les pages
du classement et les fiches détaillées.

Données récupérées :

- titre ;
- année ;
- réalisateur ;
- note presse ;
- note spectateurs ;
- URL.

Les données sont nettoyées avec un `CleanPipeline`, puis exportées dans
`films.json` et `films.csv`.


## TP 2 — Boursorama

Le spider Boursorama récupère 25 actions du palmarès français.

Données récupérées :

- libellé ;
- cours ;
- variation ;
- volume ;
- code ISIN.

Les données sont enregistrées dans la base SQLite `bourse.db`.

Le code ISIN est déclaré comme unique afin d'éviter les doublons.

## Défi 1 — Agenda parisien

 l'agenda « Que faire à Paris » de la Ville de Paris.

Contrairement à AlloCiné, certains liens apparaissent plusieurs fois et
doivent être supprimés. Les dates ne sont pas toujours dans une balise HTML
précise et doivent être recherchées dans le texte de la page.

La structure est donc un peu moins prévisible qu'AlloCiné.

Le spider récupère le titre, la date et l'URL de 25 événements dans
`evenements_paris.csv`.

## Défi 2 — Performances du crawl AlloCiné

Les tests ont été réalisés sur 50 films.

| CONCURRENT_REQUESTS | Temps | Items par seconde |
|---:|---:|---:|
| 1 | 56,86 s | 0,88 |
| 4 | 56,89 s | 0,88 |
| 8 | 56,96 s | 0,88 |
| 16 | 56,99 s | 0,88 |

Les quatre résultats sont presque identiques. Dans ce projet,
`DOWNLOAD_DELAY = 1` limite la vitesse du crawl. Augmenter le nombre de
requêtes simultanées n'apporte donc pas de gain important.

Le test avec AutoThrottle a duré 68,68 secondes. Il est plus lent sur ce
petit crawl, mais il permet d'adapter automatiquement la vitesse selon le
temps de réponse du site.

Le crawl a récupéré 50 films pour 56 réponses, soit un ratio proche de 0,89.
Un ratio inférieur à 0,5 pourrait indiquer que beaucoup de pages ne produisent
aucun résultat.

## Défi 3 — Analyse des données Boursorama

Le script `analyse_bourse.py` permet de :

- afficher les cinq principales hausses ;
- afficher les baisses lorsqu'elles existent ;
- détecter les volumes supérieurs à deux fois la moyenne ;
- exporter les données dans `analyse_bourse.csv`.

### ALTEN

ALTEN était la première hausse observée, avec environ +19,84 %.

L'entreprise a annoncé un retour à la croissance organique au deuxième
trimestre 2026 et a amélioré ses prévisions pour l'année. Cette publication
peut expliquer une partie de la hausse du cours.

### Sopra Steria

Sopra Steria affichait une hausse d'environ +13,07 %.

Le groupe a publié une progression de son chiffre d'affaires au premier
semestre 2026 et a relevé son objectif de croissance annuelle. Ces résultats
peuvent expliquer une partie de la hausse observée.

Sources consultées :

- communiqué financier ALTEN du 28 juillet 2026 ;
- résultats semestriels Sopra Steria du 29 juillet 2026.

