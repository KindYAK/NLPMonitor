from dashboard.models import DashboardPreset


def dashboard_list(request):
    if request.user.is_superuser:
        dashboards = DashboardPreset.objects.all()
    else:
        group = (hasattr(request.user, "expert") and request.user.expert.group) or \
                (hasattr(request.user, "viewer") and request.user.viewer.group)
        if not group:
            dashboards = DashboardPreset.objects.none()
        else:
            dashboards = DashboardPreset.objects.filter(usergroup=group)
    return {
        "dashboards": dashboards
    }
