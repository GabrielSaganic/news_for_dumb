from rest_framework import serializers
from scraper.models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("title",)


class SummarizedNewsSerializer(serializers.Serializer):
    content = serializers.CharField()
    title = serializers.CharField()
    url = serializers.URLField()
