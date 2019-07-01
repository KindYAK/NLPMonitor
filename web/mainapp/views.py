from django.views.generic import TemplateView


class SearchView(TemplateView):
    template_name = "mainapp/search.html"


class DashboardView(TemplateView):
    template_name = "mainapp/dashboard.html"
