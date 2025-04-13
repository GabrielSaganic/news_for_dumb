from datetime import datetime
from django.db.models import F
from django.utils.dateparse import parse_date
from log_utilis.utilis import make_logger
from rest_framework import status
from rest_framework.response import Response
from scraper.models import News
from scraper.serializers import NewsSerializer, SummarizedNewsSerializer, OverviewNewsSerializer
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from summarizer.summarizers.gpt_4o_mini import OpenAIHandler
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
        length = request.query_params.get("summary_length")
        queryset = self.get_queryset(True)

        queryset = queryset.values_list("content", flat=True)

        content = " ".join(queryset)
        # content = OpenAIHandler().overview(text=content, country="hr", overview_length=length)
        serializer = OverviewNewsSerializer({"content": content})
        return Response(serializer.data)

    def get_queryset(self, overview=False):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        tags = "" if overview else self.request.query_params.get("tags")
        categories = self.request.query_params.get("categories")
        country = self.request.query_params.get("country")

        start_date = parse_date(start_date) if start_date else datetime.today().date()
        end_date = parse_date(end_date) if end_date else datetime.today().date()
        tags = [int(tag) for tag in tags.split(",") if tags]
        categories = [int(category) for category in categories.split(",") if categories]

        if overview and len(categories) > 1:
            raise ValueError("Select only one category ni overview view.")

        filter_conditions = {
            "post_time__date__range": (start_date, end_date),
            "country": country,
        }

        if tags:
            filter_conditions.update({"tags__id__in": tags})

        if categories:
            filter_conditions.update({"category__id__in": categories})
        elif overview:
            raise ValueError("Select only one category ni overview view.")

        queryset = News.objects.filter(**filter_conditions).distinct()

        return queryset
