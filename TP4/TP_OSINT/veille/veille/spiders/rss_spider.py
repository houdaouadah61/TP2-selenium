import re
from urllib.parse import urlparse
import scrapy
from veille.items import MentionItem
CIBLES = [
    "france"
]


MOTS_NEGATIFS = [
    "fraude",
    "amende",
    "condamné",
    "condamne",
    "scandale",
    "plainte",
    "liquidation",
    "faillite",
    "perquisition",
    "accusé",
    "accuse",
    "pollution",
    "enquête",
    "enquete",
    "incendie",
    "ravage",
    "boycott"
]


MOTS_POSITIFS = [
    "croissance",
    "bénéfice",
    "benefice",
    "record",
    "acquisition",
    "innovation",
    "nomination",
    "partenariat",
    "expansion",
    "investissement",
    "accord",
    "projet",
    "gratuit",
    "autonomie",
    "rechargement"]

FLUX_RSS = [
    "https://www.lemonde.fr/rss/une.xml",
    "https://www.lefigaro.fr/rss/figaro_actualites.xml",
    "https://www.bfmtv.com/rss/info/flux-rss/flux-toutes-les-actualites/",
    "https://www.01net.com/feed/",
    (
        "https://news.google.com/rss/search"
        "?q=TotalEnergies"
        "&hl=fr"
        "&gl=FR"
        "&ceid=FR:fr"
    )
]


def nettoyer_html(texte):
    

    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = " ".join(texte.split())

    return texte


class RssSpider(scrapy.Spider):

    name = "rss_spider"

    start_urls = FLUX_RSS

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "USER_AGENT": (
            "Houda-IPSSI-OSINT/1.0 "
            "(contact: adresse.etudiante@ipssi.fr)"
        ),
        "LOG_LEVEL": "INFO"
    }

    def parse(self, response):
        

        articles = response.xpath(
            "//*[local-name()='item' or local-name()='entry']"
        )

        self.logger.info(
            "%s article(s) détecté(s) dans %s",
            len(articles),
            response.url
        )

        for article in articles:

            titre = article.xpath(
                "./*[local-name()='title']/text()"
            ).get("")

            resume = article.xpath(
                "./*[local-name()='description']/text()"
                " | ./*[local-name()='summary']/text()"
                " | ./*[local-name()='content']/text()"
            ).get("")

            titre = nettoyer_html(titre)
            resume = nettoyer_html(resume)[:300]

            texte_complet = (
                titre + " " + resume
            ).lower()

            
            mention_trouvee = False

            for cible in CIBLES:
                if cible in texte_complet:
                    mention_trouvee = True
                    break

            if not mention_trouvee:
                continue

            url = article.xpath(
                "./*[local-name()='link']/text()"
                " | ./*[local-name()='link']/@href"
            ).get("")

            url = url.strip()

            
            if not url:
                continue

            date_publication = article.xpath(
                "./*[local-name()='pubDate']/text()"
                " | ./*[local-name()='published']/text()"
                " | ./*[local-name()='updated']/text()"
            ).get("")

            date_publication = date_publication.strip()

            nombre_negatif = 0

            for mot in MOTS_NEGATIFS:
                if mot in texte_complet:
                    nombre_negatif += 1

            nombre_positif = 0

            for mot in MOTS_POSITIFS:
                if mot in texte_complet:
                    nombre_positif += 1

            if nombre_negatif > nombre_positif:
                score = 1

            elif nombre_positif > nombre_negatif:
                score = 2

            else:
                score = 0

            source = urlparse(response.url).netloc

            yield MentionItem(
                titre=titre,
                url=url,
                source=source,
                date_publi=date_publication,
                resume=resume,
                score_alerte=score
            )