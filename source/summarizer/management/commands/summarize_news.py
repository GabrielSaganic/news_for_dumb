from django.core.management.base import BaseCommand, CommandError
from log_utilis import make_logger
from scraper.models import News
from summarizer.summarizers import OpenAIHandler

logger = make_logger()


class Command(BaseCommand):
    help = "Management command for summarizing text."
    model_handlers = {
        # "bart": BartHandler
        "openai": OpenAIHandler
    }

    def add_arguments(self, parser):
        parser.add_argument("id", type=int, help="ID of the news", default=0)
        parser.add_argument(
            "model_name",
            type=str,
            help="Name of the summarizer model",
            choices=["bart", "openai"],
            default="bart",
        )

    def handle(self, *args, **options):
        id_param = options["id"]
        model_param = options["model_name"]

        handler = self.model_handlers[model_param]()

        news = News.objects.filter(id=id_param).first()

        if not news:
            raise CommandError(f"Invalid ID: {id_param}. News can not be found.")

        summarized_text = handler.summarize(news.content, news.country)

        content_list = summarized_text.split("-------------")

        print(content_list[0])
        print("-------------")
        print(content_list[1])
