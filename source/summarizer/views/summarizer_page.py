from django.views.generic import TemplateView


class SummarizerPageView(TemplateView):
    template_name = "summarizer_view.html"

class OverviewPageView(TemplateView):
    template_name = "overview_view.html"
