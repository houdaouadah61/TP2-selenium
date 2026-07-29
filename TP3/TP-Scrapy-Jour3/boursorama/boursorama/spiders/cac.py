import re

import scrapy

from boursorama.items import ActionItem


class CacSpider(scrapy.Spider):
    name = "cac"

    allowed_domains = ["boursorama.com"]

    start_urls = [
        "https://www.boursorama.com/bourse/actions/palmares/france/"
    ]

    def parse(self, response):

        # Récupération du tableau principal
        tableaux = response.css("table.c-table")

        if not tableaux:
            self.logger.error("Aucun tableau trouvé.")
            return

        tableau = tableaux[0]

        for ligne in tableau.css("tbody tr"):

            cellules = ligne.css("td.c-table__cell")

            # Le tableau doit contenir au moins 7 colonnes
            if len(cellules) < 7:
                continue

            lien = cellules[0].css("a")

            libelle = lien.xpath(
                "normalize-space(string(.))"
            ).get()

            href = lien.css("::attr(href)").get()

            cours_texte = cellules[1].xpath(
                "normalize-space(string(.))"
            ).get()

            variation_texte = cellules[2].xpath(
                "normalize-space(string(.))"
            ).get()

            volume_texte = cellules[6].xpath(
                "normalize-space(string(.))"
            ).get()

            item = ActionItem()

            item["libelle"] = libelle
            item["cours"] = self.convertir_float(cours_texte)
            item["variation"] = self.convertir_float(
                variation_texte
            )
            item["volume"] = self.convertir_volume(
                volume_texte
            )
            item["isin"] = None

            # Visite de la fiche de l'action
            if href:
                yield response.follow(
                    href,
                    callback=self.parse_action,
                    cb_kwargs={"item": item},
                )

    def parse_action(self, response, item):

        # Un ISIN contient 12 caractères
        # et se termine obligatoirement par un chiffre
        motif_isin = r"\b[A-Z]{2}[A-Z0-9]{9}\d\b"

        # Recherche prioritaire dans les titres
        isin = response.css("h2::text").re_first(
            motif_isin
        )

        # Recherche de secours dans toute la page
        if not isin:
            isin = response.xpath(
                "string(//body)"
            ).re_first(motif_isin)

        if not isin:
            self.logger.warning(
                "ISIN introuvable pour %s",
                item["libelle"],
            )
            return

        item["isin"] = isin

        yield item

    def convertir_float(self, valeur):

        if not valeur:
            return None

        valeur = valeur.replace("\xa0", "")
        valeur = valeur.replace(" ", "")
        valeur = valeur.replace("%", "")
        valeur = valeur.replace("+", "")
        valeur = valeur.replace(",", ".")

        try:
            return float(valeur)
        except ValueError:
            return None

    def convertir_volume(self, valeur):

        if not valeur:
            return None

        # Suppression de tout ce qui n'est pas un chiffre
        valeur = re.sub(r"[^\d]", "", valeur)

        if not valeur:
            return None

        try:
            return int(valeur)
        except ValueError:
            return None