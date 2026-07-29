BOT_NAME = "paris_agenda"
SPIDER_MODULES = ["paris_agenda.spiders"]
NEWSPIDER_MODULE = "paris_agenda.spiders"
ADDONS = {}
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 1

ITEM_PIPELINES = {
    "paris_agenda.pipelines.CleanPipeline": 300,
}

FEEDS = {
    "evenements_paris.csv": {
        "format": "csv",
        "encoding": "utf-8-sig",
        "overwrite": True,
        "fields": [
            "titre",
            "date",
            "url",
        ],
    },
}

LOG_LEVEL = "INFO"
