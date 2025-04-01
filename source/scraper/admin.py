from django.contrib import admin
from .models import News, Tag
from django.db.models import Count

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "post_time", "id", "url", "author", "category", "country")
    readonly_fields = ('tags',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "number_of_occurrences")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(news_count_annotation=Count('news')).order_by("-news_count_annotation")
        return queryset
