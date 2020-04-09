import datetime

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.base import View

from mainapp.services_latex import build_latex_pdf
from .services_context import get_analytics_context
from .services_plots import *


class CriterionEvalAnalysisView(TemplateView):
    template_name = "evaluation/criterion_analysis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_analytics_context(self.request, context)
        return context


class CriterionEvalAnalysisReportView(View):
    NEWS_TO_EXPORT = 25

    def preprocess_context(self, context):
        context['criterion'] = context['criterions'][0]
        context['top_documents'] = sorted(context['documents'],
                                          key=lambda x: x[context['criterion'].id],
                                          reverse=True)[:self.NEWS_TO_EXPORT]
        if context['criterion'].value_range_from < 0:
            context['bottom_documents'] = sorted(context['documents'],
                                                 key=lambda x: x[context['criterion'].id],
                                                 reverse=False)[:self.NEWS_TO_EXPORT]

    def get(self, request):
        context = get_analytics_context(self.request, {}, skip_cache=True)
        self.preprocess_context(context)
        context['title'] = datetime.datetime.now().date()
        context['request'] = request

        # Plots
        context["dynamics"] = dynamics_plot(context, request.user.id)
        context["bar_overall"] = bar_positive_negative_plot(context, request.user.id)

        pdf = build_latex_pdf("reports/analytics.tex", context)
        response = HttpResponse(content=pdf.data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=report.pdf'
        return response
