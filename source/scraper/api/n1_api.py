from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.utils.timezone import make_aware
from log_utilis import make_logger
from pytz import timezone
from scraper.models import News
from scraper.models import Category
from urllib.parse import urljoin

logger = make_logger()


class N1Api:
    def __int__(self):
        pass

    def update_news_with_detail(self, news_dict: dict) -> [str, str]:
        response = requests.get(news_dict.get("url"))
        response.encoding = "utf-8"
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        title = soup.find("h1", {"data-testid": "article-main-title"}).text.strip()
        content = self.get_news_content(soup)
        post_time = self.get_news_time(soup, news_dict.get("country"))
        author = self.get_news_author(soup)
        tags = self.get_news_tags(soup)

        news_dict["title"] = title
        news_dict["content"] = content
        news_dict["post_time"] = post_time
        news_dict["author"] = author
        news_dict["tags"] = tags

        return news_dict

    @staticmethod
    def get_news_content(soup: BeautifulSoup) -> str:
        entry_content = soup.find("article", {"data-testid": "article-wrapper"})

        # remove all related news in element
        for element in entry_content.find_all(
            attrs={"data-attribute-id": "related-news"}
        ):
            element.decompose()

        # remove N1 advertise in element
        target_link = soup.find(
            "a",
            href="https://play.google.com/store/apps/details?id=com.n1info&hl=en&pli=1",
        )
        if target_link:
            parent_p = target_link.find_parent("p")
            if parent_p:
                parent_p.decompose()

        # get only content as string
        content = [
            p.get_text(strip=True)
            for p in entry_content.find_all("p")
            if "uc-social-bar-title" not in p.get("class", [])
        ]
        content = "\n".join(content)
        content = content.replace("\n", "")
        return content

    def get_news_time(self, soup: BeautifulSoup, country: str) -> [datetime, None]:
        post_time = soup.find("div", {"data-testid": "article-published-time"})
        date = self.replace_localized_months(post_time.text.strip(), country.lower())

        try:
            news_time = datetime.strptime(date, "%d. %b. %Y. %H:%M")
            news_time = make_aware(news_time, timezone=timezone("Europe/Zagreb"))
        except ValueError:
            logger.error(
                f"Time: {date} does not match format '%d. %b. %Y. %H:%M"
            )
            return None
        except Exception as error:
            logger.error(f"Error occur when getting post time. Error: {error}")
            return None

        return news_time

    @staticmethod
    def get_news_author(soup: BeautifulSoup) -> str:
        post_author = soup.find("span", class_="author-name")
        return post_author.text.strip()

    @staticmethod
    def get_news_tags(soup: BeautifulSoup) -> list:
        tags = soup.find("a", class_="tag-block")
        return [tag.text.strip() for tag in tags]

    def n1_latest_news(self, country: str, page: int) -> [list, bool]:
        """
        Fetches the latest news articles from the N1 website for a specified country.
        :param country: The country-specific domain extension for the N1 website.
            "hr" for Croatia, "ba" for Bosnia, "rs" for Serbia.
        :param page: Page to scrape.
        :return: A list of dictionaries, where each dictionary contains:
                 - "category" (str): The category of the news.
                 - "url" (str): The URL of the news article.
        Example:
            # Output:
            # [
            #     {"category": "vijesti", "url": "https://n1info.hr/vijesti/..."},
            #     {"category": "regija", "url": "https://n1info.hr/regija/..."},
            # ]
        """
        logger.info(f"Getting latest news. Country: {country}, Page: {page}")
        base_url = f"https://n1info.{country}"
        front_page_url = urljoin(base_url, f"/najnovije/{page}/")
        response = requests.get(front_page_url)
        html_content = response.text

        news_list = []
        soup = BeautifulSoup(html_content, "html.parser")
        title_elements = soup.find_all("a", {'data-testid': 'article-upper-title'})
        for title_element in title_elements:
            news_url = urljoin(base_url, title_element.get("href"))
            logger.info(news_url)
            # TODO need to be done better, not have DB call each time
            if not News.objects.filter(url=news_url, country=country).exists():
                url_split = news_url.split("/")
                category = url_split[3]
                data = {
                    "category": self.normalize_category(category),
                    "url": news_url,
                    "country": country,
                }
                news_list.append(data)
        return news_list

    @staticmethod
    def filter_news(news_list: list, category_filter: list) -> list:
        """
        Filters a list of news articles based on specified categories.
        :param news_list: A list of dictionaries, where each dictionary represents
                          a news article and contains a "category" key.
        :param category_filter: A list of categories to filter the news articles by.
        :return: A filtered list of dictionaries containing only the news articles
                 whose "category" matches one of the categories in category_filter.
        """
        return [news for news in news_list if news.get("category") in category_filter]

    @staticmethod
    def normalize_category(category):
        if category in ["vesti", "vijesti"]:
            return Category.objects.get_or_create(name="news")[0]
        if category in ["svet", "svijet"]:
            return Category.objects.get_or_create(name="world")[0]
        if category in ["sport"]:
            return Category.objects.get_or_create(name="sport")[0]
        if category in ["region", "regija"]:
            return Category.objects.get_or_create(name="region")[0]
        if category in ["biznis"]:
            return Category.objects.get_or_create(name="business")[0]
        if category in ["magazin"]:
            return Category.objects.get_or_create(name="magazine")[0]
        if category in ["video"]:
            return Category.objects.get_or_create(name="video")[0]
        if category in ["kultura"]:
            return Category.objects.get_or_create(name="culture")[0]
        if category in ["zdravlje"]:
            return Category.objects.get_or_create(name="health")[0]
        return Category.objects.get_or_create(name=category)[0]


    @staticmethod
    def replace_localized_months(date: str, country: str) -> str:
        month_mappings = {
            "hr": {
                "sij": "Jan",
                "velj": "Feb",
                "ožu": "Mar",
                "tra": "Apr",
                "svi": "May",
                "lip": "Jun",
                "srp": "Jul",
                "kol": "Aug",
                "ruj": "Sep",
                "lis": "Oct",
                "stu": "Nov",
                "pro": "Dec",
            },
            "ba": {
                "jan": "Jan",
                "feb": "Feb",
                "mar": "Mar",
                "apr": "Apr",
                "maj": "May",
                "jun": "Jun",
                "jul": "Jul",
                "avg": "Aug",
                "sep": "Sep",
                "okt": "Oct",
                "nov": "Nov",
                "dec": "Dec",
            },
            "rs": {
                "jan": "Jan",
                "feb": "Feb",
                "mar": "Mar",
                "apr": "Apr",
                "maj": "May",
                "jun": "Jun",
                "jul": "Jul",
                "avg": "Aug",
                "sep": "Sep",
                "okt": "Oct",
                "nov": "Nov",
                "dec": "Dec",
            },
        }

        # Get the appropriate mapping based on the country
        localized_months = month_mappings.get(country.lower())
        if not localized_months:
            raise ValueError(f"Unsupported country: {country}")

        # Replace localized months with English equivalents
        for local_month, eng_month in localized_months.items():
            date = date.replace(local_month, eng_month)

        return date
