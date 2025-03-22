
import os

from django.core.management.base import BaseCommand

from log_utilis.utilis import make_logger
from ...models import News
from ...api import N1Api, S3API

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
        s3_api = S3API()

        database_downloaded = s3_api.download_from_s3(S3_BUCKET, "news_for_dumb.sqlite3", "news_for_dumb.sqlite3")
        if not database_downloaded:
            raise ConnectionError("S3 database not downloaded.")

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
            try:
                news_detail = n1_api.update_news_with_detail(news)
                News.objects.create(**news_detail)
            except Exception:
                logger.exception(
                    f"Error adding news to DB. Url: {news_detail.get('url')}"
                )
                number_of_errors = number_of_errors + 1
        database_uploaded = s3_api.upload_file_s3("news_for_dumb.sqlite3", S3_BUCKET, "news_for_dumb.sqlite3")

        if not database_uploaded:
            raise ConnectionError("S3 database not uploaded.")

        logger.info(
            f"Finish scraping latest news. Success: {len(latest_news) - number_of_errors}/{len(latest_news)}"
        )
