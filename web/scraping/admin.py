from django.contrib import admin

from .models import *


# Common
class SocialNetworkAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "social_network", "datetime_last_parsed", "priority_rate", "is_active", )
    list_filter = ("is_active", "social_network", )
    search_fields = ("name", "url", "account_id", )


# Telegram
class TelegramAuthKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "api_id", "is_active", "datetime_created", "datetime_modified", )
    list_filter = ("is_active", )
    search_fields = ("name", "api_id", "api_hash", )


# Common
admin.site.register(SocialNetworkAccount, SocialNetworkAccountAdmin)

# Telegram
admin.site.register(TelegramAuthKey, TelegramAuthKeyAdmin)
