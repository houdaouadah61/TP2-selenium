import scrapy

from allocine_scraper.items import FilmItem


class FilmsSpider(scrapy.Spider):
    name = "films"

    allowed_domains = ["allocine.fr"]

    start_urls = [
        "https://www.allocine.fr/film/meilleurs/"
    ]

    
    max_pages = 5

    def parse(self, response, page=1):

        
        films = response.css("a.meta-title-link").xpath(
            "ancestor::div[contains(@class, 'card')][1]"
        )

        for film in films:

            titre = film.css(
                "a.meta-title-link::text"
            ).get()

            lien = film.css(
                "a.meta-title-link::attr(href)"
            ).get()

            realisateur = film.css(
                ".meta-body-direction .dark-grey-link::text"
            ).get()

            note_presse = None
            note_spectateurs = None

            
            for bloc_note in film.css(".rating-item"):

                texte_note = bloc_note.xpath(
                    "normalize-space(string(.))"
                ).get() or ""

                valeur_note = bloc_note.css(
                    ".stareval-note::text"
                ).get()

                if "Presse" in texte_note:
                    note_presse = valeur_note

                if "Spectateurs" in texte_note:
                    note_spectateurs = valeur_note

            
            item = FilmItem()

            item["titre"] = titre
            item["annee"] = None
            item["realisateur"] = realisateur
            item["note_presse"] = note_presse
            item["note_spectateurs"] = note_spectateurs
            item["url"] = response.urljoin(lien)

            
            yield response.follow(
                url=item["url"],
                callback=self.parse_film,
                cb_kwargs={"item": item},
            )

        
        if page < self.max_pages:

            page_suivante = page + 1

            url_suivante = (
                "https://www.allocine.fr/film/meilleurs/"
                f"?page={page_suivante}"
            )

            yield response.follow(
                url=url_suivante,
                callback=self.parse,
                cb_kwargs={"page": page_suivante},
            )

    def parse_film(self, response, item):

        
        annee = response.css(".meta-body-info").xpath(
            "normalize-space(string(.))"
        ).re_first(r"\b(?:19|20)\d{2}\b")

        item["annee"] = annee

        yield item