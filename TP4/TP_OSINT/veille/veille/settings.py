BOT_NAME = "veille"
SPIDER_MODULES = [
    "veille.spiders"
]
NEWSPIDER_MODULE = "veille.spiders"
USER_AGENT = "Etudiante-IPSSI-OSINT/1.0"
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
ITEM_PIPELINES = {
    "veille.pipelines.CleanPipeline": 100,
    "veille.pipelines.SQLitePipeline": 200,
}

FEEDS = {
    "mentions.csv": {
        "format": "csv",
        "encoding": "utf-8",
        "overwrite": True
    }
}

FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"