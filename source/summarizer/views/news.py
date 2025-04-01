from datetime import datetime

from django.utils.dateparse import parse_date
from rest_framework.generics import ListAPIView, GenericAPIView
from scraper.models import News
from scraper.serializers import NewsSerializer, SummarizedNewsSerializer
from log_utilis.utilis import make_logger
from rest_framework.response import Response
from rest_framework import status

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

        filter_conditions = {
            "post_time__date__range": (start_date, end_date),
            "country": country,
        }

        if tags:
            filter_conditions.update({"tags__id__in": tags})
        logger.info(filter_conditions)
        queryset = News.objects.values("title").filter(**filter_conditions).distinct()

        return queryset


class SummarizedNewsView(GenericAPIView):
    serializer_class = SummarizedNewsSerializer

    def get(self, request, *args, **kwargs):
        length = self.request.query_params.get("summary_length")
        queryset = self.get_queryset()

        news_summarized_content = []
        for news in queryset:
            if length == "1":
                summary = news.content
            elif length == "2":
                summary = news.long_summary
            else:
                summary = news.short_summary

            news_summarized_content.append({"content": summary, "title": news.title, "url": news.url})

        serializer = SummarizedNewsSerializer(news_summarized_content, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        tags = self.request.query_params.get("tags")
        country = self.request.query_params.get("country")

        start_date = parse_date(start_date) if start_date else datetime.today().date()
        end_date = parse_date(end_date) if end_date else datetime.today().date()
        tags = [int(tag) for tag in tags.split(",") if tags]

        filter_conditions = {
            "post_time__date__range": (start_date, end_date),
            "country": country,
        }

        if tags:
            filter_conditions.update({"tags__id__in": tags})
        logger.info(filter_conditions)
        queryset = News.objects.filter(**filter_conditions).distinct()

        return queryset