import scrapy


class EvenementItem(scrapy.Item):
    titre = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()