import logging
import sqlite3

from itemadapter import ItemAdapter


logger = logging.getLogger(__name__)


class SQLitePipeline:

    def open_spider(self):

        # Création ou ouverture de la base
        self.connexion = sqlite3.connect("bourse.db")
        self.curseur = self.connexion.cursor()

        # Création de la table actions
        self.curseur.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libelle TEXT NOT NULL,
                cours REAL,
                variation REAL,
                volume INTEGER,
                isin TEXT NOT NULL UNIQUE,
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.connexion.commit()

    def process_item(self, item):

        action = ItemAdapter(item)

        donnees = {
            "libelle": action.get("libelle"),
            "cours": action.get("cours"),
            "variation": action.get("variation"),
            "volume": action.get("volume"),
            "isin": action.get("isin"),
        }

        self.curseur.execute(
            """
            INSERT OR IGNORE INTO actions
            (
                libelle,
                cours,
                variation,
                volume,
                isin
            )
            VALUES
            (
                :libelle,
                :cours,
                :variation,
                :volume,
                :isin
            )
            """,
            donnees,
        )

        self.connexion.commit()

        return item

    def close_spider(self):

        nombre_actions = self.curseur.execute(
            "SELECT COUNT(*) FROM actions"
        ).fetchone()[0]

        logger.info(
            "BDD : %s actions enregistrées",
            nombre_actions,
        )

        self.connexion.close()