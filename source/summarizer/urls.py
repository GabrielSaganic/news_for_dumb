from django.urls import path
from summarizer.views import TagView, SummarizerPageView, NewsView

urlpatterns = [
    path("", SummarizerPageView.as_view(), name="summarize_news"),
    path("tags/", TagView.as_view(), name="tags"),
    path("news/", NewsView.as_view(), name="news"),
]
