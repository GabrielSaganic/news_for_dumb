from rest_framework import serializers
from scraper.models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("title",)
