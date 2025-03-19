import locale
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.utils.timezone import make_aware
from pytz import timezone

from ..models import News

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class N1Api:
    def __int__(self):
        pass

    def update_news_with_detail(self, news_dict: dict) -> [str, str]:
        response = requests.get(news_dict.get("url"))
        response.encoding = "utf-8"
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        title = soup.find("h1", class_="entry-title").text.strip()

        content = self.get_news_content(soup)
        post_time = self.get_news_time(soup, news_dict.get("country"))
        author = self.get_news_author(soup)

        news_dict["title"] = title
        news_dict["content"] = content
        news_dict["post_time"] = post_time
        news_dict["author"] = author
        return news_dict

    @staticmethod
    def get_news_content(soup: BeautifulSoup) -> str:
        entry_content = soup.find("div", class_="entry-content")

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

    @staticmethod
    def get_news_time(soup: BeautifulSoup, country: str) -> [datetime, None]:
        post_time = soup.find("span", class_="post-time")
        date = post_time.find_all("span")[0].text.strip()
        time = post_time.find_all("span")[1].text.strip()
        try:
            if country.lower() == "hr":
                locale.setlocale(locale.LC_TIME, "hr_HR.UTF-8")  # Croatian locale
                tz = timezone("Europe/Zagreb")  # Croatia's timezone
            elif country.lower() == "rs":
                locale.setlocale(locale.LC_TIME, "sr_RS.UTF-8")  # Serbian locale
                tz = timezone("Europe/Belgrade")  # Serbia's timezone
            elif country.lower() == "ba":
                locale.setlocale(locale.LC_TIME, "bs_BA.UTF-8")  # Bosnian locale
                tz = timezone("Europe/Sarajevo")  # Bosnia's timezone
            else:
                raise ValueError(
                    "Unsupported country. Please specify 'Croatia', 'Serbia', or 'Bosnia'."
                )
        except locale.Error as error:
            # TODO: this need to be fixed in github action
            logging.error(f"unsupported locale setting.")
            return None

        try:
            news_time = datetime.strptime(date + " " + time, "%d. %b %Y %H:%M")
            news_time = make_aware(news_time, timezone=tz)
        except ValueError:
            logging.error(
                f"Time: {date + ' ' + time} does not match format '%d. %b %Y %H:%M"
            )
            return None
        except Exception as error:
            logging.error(f"Error occur when getting post time. Error: {error}")
            return None

        return news_time

    @staticmethod
    def get_news_author(soup: BeautifulSoup) -> str:
        post_author = soup.find("span", class_="post-author")
        return (
            post_author.find("a", class_="fn")
            .text.strip()
            .replace("Autor: ", "")
            .strip()
        )

    @staticmethod
    def get_key_word(soup: BeautifulSoup) -> list:
        # key_word = [
        #     strong.get_text(strip=True) for p in paragraphs for strong in p.find_all("strong") if "emphasized-text" not in strong.get("data-attribute-id", [])
        # ]
        #
        # content = [p.get_text(strip=True) for p in paragraphs]
        raise NotImplemented

    def n1_latest_news(self, country: str, page: int) -> [list, bool]:
        """
        Fetches the latest news articles from the N1 website for a specified country.
        :param country: The country-specific domain extension for the N1 website.
            "hr" for Croatia, "ba" for Bosnia, "rs" for Serbia.
        :param page: Page to scrape.
        :return: A list of dictionaries, where each dictionary contains:
                 - "category" (str): The category of the news.
                 - "url" (str): The URL of the news article.
                 A boolean value if all latest news are scraped.
        Example:
            # Output:
            # [
            #     {"category": "vijesti", "url": "https://n1info.hr/vijesti/..."},
            #     {"category": "regija", "url": "https://n1info.hr/regija/..."},
            # ]
        """
        logging.info(f"Getting latest news. Country: {country}, Page: {page}")
        url = f"https://n1info.{country}/najnovije/page/{page}"
        response = requests.get(url)
        html_content = response.text

        news_list = []
        soup = BeautifulSoup(html_content, "html.parser")
        title_elements = soup.find_all("a", class_="uc-block-post-grid-title-link")
        all_news_scraped = False
        for title_element in title_elements:
            url = title_element.get("href")
            # TODO need to be done better, not have DB call each time
            if not News.objects.filter(url=url, country=country).exists():
                url_split = url.split("/")
                category = url_split[3]
                data = {
                    "category": self.normalize_category(category),
                    "url": url,
                    "country": country,
                }
                news_list.append(data)
            else:
                all_news_scraped = True
        return news_list, all_news_scraped

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
            return "news"
        if category in ["svet", "svijet"]:
            return "world"
        if category in ["sport"]:
            return "sport"
        if category in ["region", "regija"]:
            return "region"
        if category in ["biznis"]:
            return "business"
        if category in ["magazin"]:
            return "magazine"
        if category in ["video"]:
            return "video"
        if category in ["kultura"]:
            return "kultura"
        if category in ["zdravlje"]:
            return "health"
        logging.error(f"Not know category: {category}.")
        return ""
