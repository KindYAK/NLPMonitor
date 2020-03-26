from annoying.functions import get_object_or_None
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.views.generic import TemplateView

from mainapp.services import get_user_group
from .models import DashboardPreset


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dashboard_id = kwargs['dashboard_id']
        if not self.request.user.is_superuser:
            group = get_user_group(self.request.user)
            if not group:
                return context
            dashboards = group.dashboard_presets.all()
        else:
            dashboards = DashboardPreset.objects.all()

        if dashboard_id == 0:
            context['dashboard_template'] = dashboards.first()
        else:
            context['dashboard_template'] = get_object_or_None(DashboardPreset, id=dashboard_id)
        if context['dashboard_template'] not in dashboards:
            return context

        def widget_cache_hit_wrapper(dashboard_template, widget):
            key = make_template_fragment_key('widget', [dashboard_template.topic_modelling_name, widget.id])
            if cache.get(key):
                return {}
            return widget.callable(dashboard_template, widget)

        context['widgets'] = context['dashboard_template'].widgets.all().order_by('index')
        # Fill widget context
        for widget in context['widgets']:
            context.update(widget_cache_hit_wrapper(context['dashboard_template'], widget))
        return context
