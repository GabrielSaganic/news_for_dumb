from django.urls import path
from summarizer.views import TagView, SummarizerPageView, NewsView, SummarizedNewsView

urlpatterns = [
    path("", SummarizerPageView.as_view(), name="summarizer"),
    path("tags/", TagView.as_view(), name="tags"),
    path("news/", NewsView.as_view(), name="news"),
    path("summarize_news/", SummarizedNewsView.as_view(), name="summarize-news"),

]
