import logging
import sqlite3
from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)


CREATION_TABLE = """
CREATE TABLE IF NOT EXISTS mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    url TEXT UNIQUE,
    source TEXT,
    date_publi TEXT,
    resume TEXT,
    score_alerte INTEGER DEFAULT 0,
    date_scraping TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


class CleanPipeline:
    

    def process_item(self, item):
        donnees = ItemAdapter(item)

        donnees["titre"] = donnees.get(
            "titre",
            ""
        ).strip()

        donnees["resume"] = donnees.get(
            "resume",
            ""
        ).strip()[:300]

        return item


class SQLitePipeline:
    

    def open_spider(self):
        self.connexion = sqlite3.connect(
            "veille.db"
        )

        self.connexion.execute(
            CREATION_TABLE
        )

        self.connexion.commit()

    def process_item(self, item):
        donnees = ItemAdapter(item)

        try:
            self.connexion.execute(
                """
                INSERT OR IGNORE INTO mentions
                (
                    titre,
                    url,
                    source,
                    date_publi,
                    resume,
                    score_alerte
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    donnees.get("titre", ""),
                    donnees.get("url", ""),
                    donnees.get("source", ""),
                    donnees.get("date_publi", ""),
                    donnees.get("resume", ""),
                    donnees.get("score_alerte", 0)
                )
            )

            self.connexion.commit()

        except sqlite3.Error as erreur:
            logger.error(
                "Erreur SQLite : %s",
                erreur
            )

        return item

    def close_spider(self):
        nombre = self.connexion.execute(
            "SELECT COUNT(*) FROM mentions"
        ).fetchone()[0]

        logger.info(
            "%s mention(s) enregistrée(s)",
            nombre
        )

        self.connexion.close()