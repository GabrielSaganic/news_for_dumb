from datetime import datetime

from django.utils.dateparse import parse_date
from rest_framework.generics import ListAPIView
from scraper.models import Category
from scraper.serializers import CategorySerializer


class CategoryView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        country = self.request.query_params.get("country")

        start_date = parse_date(start_date) if start_date else datetime.today().date()
        end_date = parse_date(end_date) if end_date else datetime.today().date()

        queryset = Category.get_top_10_by_date(country, start_date, end_date)
        return queryset
