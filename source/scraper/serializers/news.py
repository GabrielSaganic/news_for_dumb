from rest_framework import serializers
from scraper.models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("title",)


class SummarizedNewsSerializer(serializers.Serializer):
    summary_text = serializers.CharField()
    title = serializers.CharField()
    url = serializers.URLField()

class NewsDetailSerializer(serializers.Serializer):
    url = serializers.URLField()
    title = serializers.CharField()

class OverviewNewsSerializer(serializers.Serializer):
    content = serializers.CharField()
    news_detail = NewsDetailSerializer(many=True)

class QueryParamsOverviewSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    country = serializers.CharField(required=False)
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    keyword = serializers.CharField(required=False)

    def validate(self, data):
        categories = data.get("categories", [])
        key_word = data.get("keyword", "")

        if not categories and not key_word:
            raise serializers.ValidationError({"detail": "Select either category or key word in overview view."})

        if len(categories) > 1:
            raise serializers.ValidationError({"detail": "Select only one category in overview view."})

        return data
