import sqlite3


connexion = sqlite3.connect("veille.db")
curseur = connexion.cursor()

articles = curseur.execute(
    """
    SELECT id, titre, url, resume, score_alerte
    FROM mentions
    ORDER BY id
    """
).fetchall()

print("Nombre total d'articles :", len(articles))

for article in articles:
    identifiant = article[0]
    titre = article[1]
    url = article[2]
    resume = article[3]
    score = article[4]

    print("\n------------------------------")
    print("ID :", identifiant)
    print("Score :", score)
    print("Titre :", titre)
    print("Résumé :", resume)
    print("URL :", url)

connexion.close()