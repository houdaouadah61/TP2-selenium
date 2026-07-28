# Défi 1 - Cookie forensics

## Test d'injection du consentement Doctolib

| Test | Cookies injectés | Bannière présente |
|---|---|---|
| sans_cookie | Aucun | Oui |
| didomi_token_seul | didomi_token | Non |
| euconsent_v2_seul | euconsent-v2 | Oui |
| deux_cookies | didomi_token, euconsent-v2 | Non |

Le premier scénario qui masque la bannière est : didomi_token.

Les valeurs complètes des cookies ne sont pas recopiées dans le rapport.

## Cookies de domaines tiers détectés

| Nom | Domaine | Durée | Valeur encodée |
|---|---|---|---|
| __cf_bm | .doctolib.fr | Session | Oui |

## Cookies liés à des services externes

Ces cookies sont déposés sur les domaines des sites, mais leur fonction est assurée par un service externe.

| Nom | Site observé | Domaine | Durée | Valeur encodée |
|---|---|---|---|---|
| __cf_bm | Doctolib | .doctolib.fr | Expiré | Oui |
| datadome | Maiia | .maiia.com | 365 jours | Oui |
| dtCookie | Maiia | .maiia.com | Session | Oui |

## Comparaison Doctolib / Maiia

- Doctolib utilise `didomi_token` et `euconsent-v2` pour le consentement.
- Les mêmes noms n'ont pas été trouvés sur Maiia.
- Maiia a notamment créé des cookies liés à la sécurité et à la mesure technique.

## Limite

`driver.get_cookies()` ne retourne que les cookies du domaine courant. Le script utilise donc aussi le protocole DevTools de Chrome pour rechercher les cookies du profil complet.
