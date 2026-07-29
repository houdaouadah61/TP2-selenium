
BOT_NAME = "allocine_scraper"

SPIDER_MODULES = ["allocine_scraper.spiders"]
NEWSPIDER_MODULE = "allocine_scraper.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = True


CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
DEFAULT_REQUEST_HEADERS = {
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}
ITEM_PIPELINES = {
    "allocine_scraper.pipelines.CleanPipeline": 300,
}
FEEDS = {
    "films.json": {
        "format": "json",
        "encoding": "utf-8",
        "indent": 2,
        "overwrite": True,
    },
    "films.csv": {
        "format": "csv",
        "encoding": "utf-8-sig",
        "overwrite": True,
    },
}
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
LOG_LEVEL = "INFO"