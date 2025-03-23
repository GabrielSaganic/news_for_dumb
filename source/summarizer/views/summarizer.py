from datetime import datetime

from django.utils.dateparse import parse_date
from rest_framework.generics import ListAPIView
from scraper.models import Tag
from scraper.serializers import TagSerializer


class TagView(ListAPIView):
    serializer_class = TagSerializer

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        start_date = parse_date(start_date) if start_date else datetime.today().date()
        end_date = parse_date(end_date) if end_date else datetime.today().date()

        queryset = Tag.get_top_10_by_date(start_date, end_date)
        return queryset
