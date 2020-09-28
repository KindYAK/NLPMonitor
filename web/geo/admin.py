from django.contrib import admin

from geo.models import Locality, District, Area


class AreaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ()
    search_fields = ('name',)


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ()
    search_fields = ('name',)


class LocalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'kato_code', 'district', 'latitude', 'longitude')
    list_filter = ()
    search_fields = ('name',)


admin.site.register(Area, AreaAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Locality, LocalityAdmin)
