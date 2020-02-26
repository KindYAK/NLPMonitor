from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test_widget_arg'] = "Test - shmest"
        return context
