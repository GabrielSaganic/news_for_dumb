from datetime import datetime

from django.utils.dateparse import parse_date
from rest_framework.generics import ListAPIView
from scraper.models import News
from scraper.serializers import NewsSerializer
from log_utilis.utilis import make_logger

logger = make_logger()


class NewsView(ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        tags = self.request.query_params.get("tags")
        country = self.request.query_params.get("country")

        start_date = parse_date(start_date) if start_date else datetime.today().date()
        end_date = parse_date(end_date) if end_date else datetime.today().date()
        tags = [int(tag) for tag in tags.split(",") if tags]

        logger.info(start_date)
        logger.info(end_date)
        logger.info(tags)

        filter_conditions = {
            "post_time__date__range": (start_date, end_date),
            "country": country,
        }

        if tags:
            filter_conditions.update({"tags__id__in": tags})

        queryset = News.objects.values("title").filter(**filter_conditions)
        return queryset
