from annoying.functions import get_object_or_None
from django.views.generic import TemplateView

from .models import DashboardPreset


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def form_management(self, context):
        context['dashboards'] = DashboardPreset.objects.all()
        if not self.request.user.is_superuser:
            group = (hasattr(self.request.user, "expert") and self.request.user.expert.group) or \
                    (hasattr(self.request.user, "viewer") and self.request.user.viewer.group)
            if not group:
                context['dashboards'] = context['dashboards'].none()
            else:
                context['dashboards'] = context['dashboards'].filter(usergroup=group)
        dashboard_id = self.request.GET.get("dashboard_id", None)
        if dashboard_id:
            context['dashboard_template'] = get_object_or_None(DashboardPreset, id=dashboard_id)
        else:
            context['dashboard_template'] = context['dashboards'].first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.form_management(context)
        if not context['dashboard_template']:
            return context
        context['widgets'] = context['dashboard_template'].widgets.all().order_by('index')
        # Fill widget context
        for widget in context['widgets']:
            context.update(widget.callable(context['dashboard_template'], widget))
        return context
