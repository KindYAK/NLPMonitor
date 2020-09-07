from dashboard.models import DashboardPreset
from mainapp.services import get_user_group


def dashboard_list(request):
    if request.user.is_superuser:
        dashboards = DashboardPreset.objects.all()
    else:
        group = get_user_group(request.user)
        if not group:
            dashboards = DashboardPreset.objects.none()
        else:
            dashboards = DashboardPreset.objects.filter(usergroup=group)
    return {
        "dashboards": dashboards
    }
