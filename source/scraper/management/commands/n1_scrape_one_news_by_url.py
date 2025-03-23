import os
import re

from django.core.management.base import BaseCommand, CommandError
from log_utilis import make_logger
from scraper.api import N1Api
from scraper.models import News, Tag

logger = make_logger()

S3_BUCKET = os.environ.get("S3_BUCKET", "")


class Command(BaseCommand):
    help = "Management command for scraping latest news from N1 portal."

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="URL of the news", default="")

    def handle(self, *args, **options):
        n1_api = N1Api()
        url_param = options["url"]

        if News.objects.filter(url=url_param).exists():
            logger.info(f"News: {url_param} already scraped.")
            return None

        country_match = re.search(r"n1info\.(\w\w)", url_param)
        if not country_match:
            raise CommandError(
                f"Invalid URL: {url_param}. Country code can not be extracted."
            )

        news = {
            "url": url_param,
            "country": country_match.group(1),
            "category": n1_api.normalize_category(url_param.split("/")[3]),
        }

        logger.info(f"Started fetching news: {news.get('url')}")
        try:
            news_detail = n1_api.update_news_with_detail(news)
            tags_list = []
            for tag in news_detail.pop("tags", []):
                tags_list.append(Tag.objects.get_or_create(name=tag)[0])
            news = News.objects.create(**news_detail)
            news.tags.add(*tags_list)
        except Exception:
            logger.exception(f"Error adding news to DB. Url: {url_param}")
        logger.info(f"Finish scraping news: {url_param}.")
