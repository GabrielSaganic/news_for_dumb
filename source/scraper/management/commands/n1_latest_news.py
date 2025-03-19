import logging

from django.core.management.base import BaseCommand

from ...models import News
from ...news_api.n1_api import N1Api

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


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
        logging.info(
            f"Starting n1 scrape with params: Country {countries_param}, Category: {category_param}, Page: {page_param}"
        )
        for country_param in countries_param:
            for i in range(1, page_param + 1):
                try:
                    news, all_news_scraped = n1_api.n1_latest_news(country_param, i)
                except Exception:
                    logging.exception(f"Error scraping latest news.")
                latest_news = latest_news + news
                if all_news_scraped:
                    break
        logging.info(
            f"Successfully get all latest news. Number of news: {len(latest_news)}"
        )

        if category_param:
            n1_api.filter_news(latest_news, category_param)

        number_of_errors = 0
        for news in latest_news:
            logging.info(f"Started fetching news: {news.get('url')}")
            try:
                news_detail = n1_api.update_news_with_detail(news)
                News.objects.create(**news_detail)
            except Exception:
                logging.exception(
                    f"Error adding news to DB. Url: {news_detail.get('url')}"
                )
                number_of_errors = number_of_errors + 1
        logging.info(
            f"Finish scraping latest news. Success: {len(latest_news) - number_of_errors}/{len(latest_news)}"
        )
