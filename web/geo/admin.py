from django.contrib import admin

from geo.models import Locality, District, Area


class AreaAdmin(admin.ModelAdmin):
    list_display = ('area_name',)
    list_filter = ()
    search_fields = ('area_name',)


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('district_name',)
    list_filter = ()
    search_fields = ('district_name',)


class LocalityAdmin(admin.ModelAdmin):
    list_display = ('locality_name', 'kato_code', 'district', 'latitude', 'longitude')
    list_filter = ()
    search_fields = ('locality_name',)


admin.site.register(Area, AreaAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Locality, LocalityAdmin)
