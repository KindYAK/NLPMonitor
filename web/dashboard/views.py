from annoying.functions import get_object_or_None
from django.views.generic import TemplateView

from .models import DashboardPreset


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dashboard_id = kwargs['dashboard_id']
        if dashboard_id == 0:
            context['dashboard_template'] = DashboardPreset.objects.first()
        else:
            context['dashboard_template'] = get_object_or_None(DashboardPreset, id=dashboard_id)
        if not self.request.user.is_superuser:
            group = (hasattr(self.request.user, "expert") and self.request.user.expert.group) or \
                    (hasattr(self.request.user, "viewer") and self.request.user.viewer.group)
            if not group or context['dashboard_template'] not in group.dashboard_presets.all():
                return context
        if not context['dashboard_template']:
            return context
        context['widgets'] = context['dashboard_template'].widgets.all().order_by('index')
        # Fill widget context
        for widget in context['widgets']:
            context.update(widget.callable(context['dashboard_template'], widget))
        return context
