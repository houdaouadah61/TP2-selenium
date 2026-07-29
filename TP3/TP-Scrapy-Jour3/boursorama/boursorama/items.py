import scrapy


class ActionItem(scrapy.Item):
    libelle = scrapy.Field()
    cours = scrapy.Field()
    variation = scrapy.Field()
    volume = scrapy.Field()
    isin = scrapy.Field()