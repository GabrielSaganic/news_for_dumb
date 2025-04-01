from datetime import datetime

from django.db import models
from django.db.models import Count


class News(models.Model):
    COUNTRY_CHOICES = [
        ("ba", "Bosnia and Herzegovina"),
        ("hr", "Croatia"),
        ("rs", "Serbia"),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    long_summary = models.TextField(blank=True, null=True)
    short_summary = models.TextField(blank=True, null=True)
    post_time = models.DateTimeField(blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, blank=True, null=True
    )
    url = models.URLField(max_length=500, unique=True)
    tags = models.ManyToManyField("tag")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    @property
    def number_of_occurrences(self):
        return self.news_set.count()

    @staticmethod
    def get_today_top_10():
        today = datetime.today()
        return (
            Tag.objects.filter(news__post_time__date=today)
            .annotate(news_count=Count("news"))
            .order_by("-news_count")[:10]
        )

    @staticmethod
    def get_top_10_by_date(country, start_date, end_date):
        return (
            Tag.objects.filter(
                news__post_time__date__range=(start_date, end_date),
                news__country=country,
            )
            .annotate(news_count=Count("news"))
            .order_by("-news_count")[:10]
        )
