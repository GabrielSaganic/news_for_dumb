from django.urls import path
from summarizer.views import NewsViewSet,  SummarizerPageView, TagView


urlpatterns = [
    path("", SummarizerPageView.as_view(), name="summarizer"),
    path("tags/", TagView.as_view(), name="tags"),
    path("news/", NewsViewSet.as_view({'get': 'list_news'}), name="news"),
    path("summarize_news/", NewsViewSet.as_view({'get': 'summarize_news'}), name="summarize-news"),
]
