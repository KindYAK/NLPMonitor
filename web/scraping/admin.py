from django.contrib import admin

from .models import *


# Common
class SocialNetworkAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "account_id", "social_network", "datetime_last_parsed", "priority_rate", "is_active", "is_private", "is_valid", )
    list_filter = ("is_active", "social_network", "is_private", "is_valid", )
    search_fields = ("name", "url", "account_id", )


# Telegram
class TelegramAuthKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "api_id", "is_active", "datetime_created", "datetime_modified", )
    list_filter = ("is_active", )
    search_fields = ("name", "api_id", "api_hash", )


# Instagram
class InstagramLoginPassAdmin(admin.ModelAdmin):
    list_display = ("login", "is_active", "datetime_created", "datetime_modified", )
    list_filter = ("is_active", )
    search_fields = ("login", )


# Common
admin.site.register(SocialNetworkAccount, SocialNetworkAccountAdmin)

# Telegram
admin.site.register(TelegramAuthKey, TelegramAuthKeyAdmin)

# Instagram
admin.site.register(InstagramLoginPass, InstagramLoginPassAdmin)
