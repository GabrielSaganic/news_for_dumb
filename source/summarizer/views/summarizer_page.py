from django.views.generic import TemplateView


class SummarizerPageView(TemplateView):
    template_name = "summarizer_view.html"
