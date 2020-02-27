from django.views.generic import TemplateView

from .models import DashboardPreset


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dashboard_template'] = DashboardPreset.objects.get(id=kwargs['dashboard_id'])
        context['widgets'] = context['dashboard_template'].widgets.all().order_by('index')
        # Fill widget context
        for widget in context['widgets']:
            context.update(widget.callable(widget))
        return context
