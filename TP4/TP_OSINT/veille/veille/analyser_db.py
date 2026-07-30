import sqlite3
try:
    
    connexion = sqlite3.connect("veille.db")
    curseur = connexion.cursor()

    
    resultats = curseur.execute(
        """
        SELECT titre, source, score_alerte
        FROM mentions
        ORDER BY score_alerte DESC
        """
    ).fetchall()

    print(
        "Nombre de mentions trouvées :",
        len(resultats)
    )

    if len(resultats) == 0:
        print(
            "Aucun article ne mentionne la cible "
            "dans les flux actuels."
        )

    else:
        print("\nPremières mentions :")

        for resultat in resultats[:5]:
            titre = resultat[0]
            source = resultat[1]
            score = resultat[2]

            print(
                "[",
                score,
                "]",
                titre[:70],
                "-",
                source
            )

    connexion.close()

except sqlite3.Error as erreur:
    print(
        "Erreur SQLite :",
        erreur
    )