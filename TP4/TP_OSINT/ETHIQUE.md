TD 4.1 — Empreinte d’un domaine

1. Ai-je le droit ?

Oui, car j’utilise seulement des sources publiques:

WHOIS ;

les headers HTTP ;

le fichier robots.txt ;

l’adresse IP ;

les certificats publics avec crt.sh.

Je ne me connecte pas à une partie privée du site et je ne contourne aucune authentification.

2. Est-ce personnel ?

Non, car je récupère surtout des informations techniques sur un domaine et un serveur.

Le WHOIS peut parfois afficher un nom ou une adresse e-mail. Je ne dois pas utiliser ces informations pour contacter ou surveiller une personne.

3. Suis-je discret ?

Oui.

J’utilise un User-Agent identifiable et j’ajoute une pause entre les requêtes.Je limite aussi le nombre de tentatives quand un service ne répond pas.

Pendant mon test sur ipssi.fr, crt.sh ne répondait pas correctement. Le résultat affichait donc zéro sous-domaine, mais cela ne veut pas dire qu’il n’existe aucun sous-domaine.

TD 4.2 — Cartographie d’une entreprise

1. Ai-je le droit ?

Oui, car j’utilise des sources publiques :

l’API officielle de recherche des entreprises ;

Wikipédia ;

des flux RSS de presse.

Je n’utilise pas de compte privé et je ne contourne pas de protection.

2. Est-ce personnel ?

Non, car mon travail porte sur une entreprise publique.

Je récupère des informations comme le SIREN, l’adresse du siège, l’activité, la présentation Wikipédia et des articles de presse.

Je ne cherche pas à faire un profil sur une personne précise.

3. Suis-je discret ?

Oui.

J’utilise un User-Agent identifiable et j’attends au moins une seconde entre les requêtes.

Je limite aussi le nombre d’articles récupérés. Les résultats sont enregistrés seulement dans un fichier JSON sur mon ordinateur.

TD 4.3 — Veille RSS avec Scrapy

1. Ai-je le droit ?

Oui, car le spider consulte seulement des flux RSS publics.

Scrapy respecte le fichier robots.txt. Pendant mon test, un flux a été refusé et le spider n’a pas essayé de contourner ce refus.

2. Est-ce personnel ?

Non.

Le spider enregistre seulement des informations sur des articles publics :

le titre ;

l’URL ;

la source ;

la date ;

le résumé ;

le score d’alerte.

Je ne récupère pas de mot de passe, de compte privé ou d’adresse personnelle.

3. Suis-je discret ?

Oui.

J’ai configuré :

un délai d’au moins une seconde ;

une seule requête à la fois par domaine ;

un User-Agent identifiable ;

le respect de robots.txt ;

une base SQLite qui évite les doublons grâce à l’URL unique.
