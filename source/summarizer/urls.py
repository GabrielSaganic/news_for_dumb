from django.urls import path
from summarizer.views import TagView

urlpatterns = [
    path("", TagView.as_view(), name="summarize_news"),
]
