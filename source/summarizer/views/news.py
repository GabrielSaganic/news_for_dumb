import time
from datetime import datetime
from django.db.models import F
from django.utils.dateparse import parse_date
from log_utilis.utilis import make_logger
from rest_framework import status
from rest_framework.response import Response
from scraper.models import News
from scraper.serializers import NewsSerializer, SummarizedNewsSerializer, OverviewNewsSerializer, QueryParamsOverviewSerializer
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from summarizer.summarizers.gpt_4o_mini import OpenAIHandler
from django.db.models import Q

logger = make_logger()

class NewsViewSet(ViewSet):
    @action(detail=False, methods=['get'], url_path='list_news')
    def list_news(self, _):
        queryset = self.get_queryset()
        serializer = NewsSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='summarize_news')
    def summarize_news(self, request):
        length = request.query_params.get("summary_length")
        queryset = self.get_queryset()

        if length == "1":
            queryset = queryset.annotate(summary_text=F('content'))
        elif length == "2":
            queryset = queryset.exclude(long_summary__isnull=True).annotate(summary_text=F('long_summary'))
        else:
            queryset = queryset.exclude(short_summary__isnull=True).annotate(summary_text=F('short_summary'))

        queryset = queryset.values("summary_text", "title", "url")

        serializer = SummarizedNewsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='overview_news')
    def overview_news(self, request):
        serializer = QueryParamsOverviewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        length = request.query_params.get("summary_length")
        country = self.request.query_params.get("country")

        queryset = self.get_queryset().exclude(long_summary__isnull=True)

        if queryset.count() > 10:
            return Response({"detail": "Can't summarize more then 10 news."}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        news_detail = queryset.values("title", "url")
        content_queryset = queryset.values_list("long_summary", flat=True)

        content = " ".join(content_queryset)
        content = OpenAIHandler().overview(text=content, country=country, overview_length=length)
        serializer = OverviewNewsSerializer({"content": content, "news_detail": news_detail})
        return Response(serializer.data)

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        tags = self.request.query_params.get("tags", "")
        categories = self.request.query_params.get("categories", "")
        country = self.request.query_params.get("country")
        key_word = self.request.query_params.get("keyword")

        start_date = parse_date(start_date) if start_date else datetime.today().date()
        end_date = parse_date(end_date) if end_date else datetime.today().date()

        tags = [int(tag) for tag in tags.split(",") if tags]
        categories = [int(category) for category in categories.split(",") if categories]

        filter_conditions = {
            "post_time__date__range": (start_date, end_date),
            "country": country,
        }

        if tags:
            filter_conditions.update({"tags__id__in": tags})

        if key_word:
            filter_conditions.update({"content__icontains": key_word})

        if categories:
            filter_conditions.update({"category__id__in": categories})


        queryset = News.objects.filter(**filter_conditions).distinct()

        return queryset
