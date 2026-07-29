import csv
import sqlite3
from pathlib import Path


# Chemins des fichiers
dossier = Path(__file__).resolve().parent
chemin_base = dossier / "bourse.db"
chemin_csv = dossier / "analyse_bourse.csv"


# Connexion à SQLite
connexion = sqlite3.connect(chemin_base)
curseur = connexion.cursor()


# Top 5 des hausses
hausses = curseur.execute(
    """
    SELECT libelle, variation, cours
    FROM actions
    WHERE variation > 0
    ORDER BY variation DESC
    LIMIT 5
    """
).fetchall()

print("\nTOP 5 DES HAUSSES")

if hausses:
    for libelle, variation, cours in hausses:
        print(
            f"{libelle} : {variation:+.2f}% "
            f"| cours : {cours}"
        )
else:
    print("Aucune hausse dans les données collectées.")


# Top 5 des baisses
baisses = curseur.execute(
    """
    SELECT libelle, variation, cours
    FROM actions
    WHERE variation < 0
    ORDER BY variation ASC
    LIMIT 5
    """
).fetchall()

print("\nTOP 5 DES BAISSES")

if baisses:
    for libelle, variation, cours in baisses:
        print(
            f"{libelle} : {variation:+.2f}% "
            f"| cours : {cours}"
        )
else:
    print("Aucune baisse dans les données collectées.")


# Volumes supérieurs à deux fois la moyenne
volumes_eleves = curseur.execute(
    """
    SELECT libelle, volume, cours
    FROM actions
    WHERE volume > (
        SELECT AVG(volume) * 2
        FROM actions
    )
    ORDER BY volume DESC
    """
).fetchall()

print("\nVOLUMES ÉLEVÉS")

if volumes_eleves:
    for libelle, volume, cours in volumes_eleves:
        print(
            f"{libelle} : volume {volume} "
            f"| cours : {cours}"
        )
else:
    print("Aucun volume élevé trouvé.")


# Données pour le CSV
actions = curseur.execute(
    """
    SELECT
        libelle,
        cours,
        variation,
        volume,
        isin,
        scraped_at
    FROM actions
    ORDER BY variation DESC
    """
).fetchall()


# Export CSV
with open(
    chemin_csv,
    "w",
    newline="",
    encoding="utf-8-sig",
) as fichier:

    writer = csv.writer(
        fichier,
        delimiter=";",
    )

    writer.writerow(
        [
            "libelle",
            "cours",
            "variation",
            "volume",
            "isin",
            "scraped_at",
        ]
    )

    writer.writerows(actions)


connexion.close()

print("\nFichier créé :", chemin_csv)