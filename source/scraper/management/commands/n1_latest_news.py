import os

from django.core.management.base import BaseCommand
from log_utilis import make_logger
from scraper.api import N1Api
from scraper.models import News, Tag

logger = make_logger()

S3_BUCKET = os.environ.get("S3_BUCKET", "")


class Command(BaseCommand):
    help = "Management command for scraping latest news from N1 portal."

    def add_arguments(self, parser):
        parser.add_argument(
            "--country",
            nargs="+",
            type=str,
            help="Filter news by country",
            default=["hr", "rs", "ba"],
        )
        parser.add_argument(
            "--category", type=int, help="Filter news by category", default=[]
        )
        parser.add_argument(
            "--page", type=int, help="How many page to scrape", default=50
        )

    def handle(self, *args, **options):
        n1_api = N1Api()
        countries_param = options["country"]
        category_param = options["category"]
        page_param = options["page"]

        latest_news = []
        news = []
        all_news_scraped = False

        logger.info(
            f"Starting n1 scrape with params: Country {countries_param}, Category: {category_param}, Page: {page_param}"
        )
        for country_param in countries_param:
            for i in range(1, page_param + 1):
                try:
                    news, all_news_scraped = n1_api.n1_latest_news(country_param, i)
                except Exception:
                    logger.exception(f"Error scraping latest news.")
                latest_news = latest_news + news
                if all_news_scraped:
                    break
        logger.info(
            f"Successfully get all latest news. Number of news: {len(latest_news)}"
        )

        if category_param:
            n1_api.filter_news(latest_news, category_param)

        number_of_errors = 0
        for news in latest_news:
            logger.info(f"Started fetching news: {news.get('url')}")
            news_detail = {}
            try:
                news_detail = n1_api.update_news_with_detail(news)
                tags_list = []
                for tag in news_detail.pop("tags", []):
                    tags_list.append(Tag.objects.get_or_create(name=tag)[0])
                news = News.objects.create(**news_detail)
                news.tags.add(*tags_list)
            except Exception:
                logger.exception(
                    f"Error adding news to DB. Url: {news_detail.get('url')}"
                )
                number_of_errors = number_of_errors + 1

        logger.info(
            f"Finish scraping latest news. Success: {len(latest_news) - number_of_errors}/{len(latest_news)}"
        )
