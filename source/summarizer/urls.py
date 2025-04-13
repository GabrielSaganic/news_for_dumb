from django.urls import path
from summarizer.views import NewsViewSet,  SummarizerPageView, TagView, CategoryView, OverviewPageView


urlpatterns = [
    path("", SummarizerPageView.as_view(), name="summarizer"),
    path("overview", OverviewPageView.as_view(), name="overview"),
    path("news-overview/", NewsViewSet.as_view({'get': 'overview_news'}), name="overview-news"),
    path("tags/", TagView.as_view(), name="tags"),
    path("news/", NewsViewSet.as_view({'get': 'list_news'}), name="news"),
    path("categories/", CategoryView.as_view(), name="categories"),
    path("summarize_news/", NewsViewSet.as_view({'get': 'summarize_news'}), name="summarize-news"),
]
