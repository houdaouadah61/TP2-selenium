import re

import scrapy

from paris_agenda.items import EvenementItem


class EvenementsSpider(scrapy.Spider):
    name = "evenements"

    allowed_domains = ["paris.fr"]

    start_urls = [
        "https://www.paris.fr/quefaire"
    ]

    max_evenements = 25

    def parse(self, response):

        liens = response.css(
            'a[href^="/evenements/"]::attr(href)'
        ).getall()

        
        liens_uniques = list(dict.fromkeys(liens))

        for lien in liens_uniques[:self.max_evenements]:

            yield response.follow(
                lien,
                callback=self.parse_evenement,
            )

    def parse_evenement(self, response):

        titre = response.css("h1::text").get()

        texte_principal = response.xpath(
            "normalize-space(string(//main))"
        ).get() or ""

        
        resultat_date = re.search(
            r"\b(?:Du|Le)\s+.{1,120}?\b20\d{2}\b",
            texte_principal,
            re.IGNORECASE,
        )

        date = None

        if resultat_date:
            date = resultat_date.group(0)

        yield EvenementItem(
            titre=titre,
            date=date,
            url=response.url,
        )