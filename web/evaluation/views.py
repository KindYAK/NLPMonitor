import datetime

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.base import View

from mainapp.services_latex import build_latex_pdf
from .services_context import get_analytics_context


class CriterionEvalAnalysisView(TemplateView):
    template_name = "evaluation/criterion_analysis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_analytics_context(self.request, context)
        return context


class CriterionEvalAnalysisReportView(View):
    def get(self, request):
        context = get_analytics_context(self.request, {}, skip_cache=True)
        context['title'] = datetime.datetime.now().date()
        context['request'] = request
        pdf = build_latex_pdf("reports/analytics.tex", context)
        response = HttpResponse(content=pdf.data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=report.pdf'
        return response
