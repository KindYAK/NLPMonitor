from django.contrib import admin

from .models import *


# Common
class SocialNetworkAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "account_id", "social_network", "datetime_last_parsed", "priority_rate", "is_active",
                    "is_private", "is_valid", "keywords", "description", "topic_ids", "view_count", "posts_count")
    list_filter = ("is_active", "social_network", "is_private", "is_valid", )
    search_fields = ("name", "url", "account_id", )


class MonitoringQueryAdmin(admin.ModelAdmin):
    list_display = ("name", "query", "social_network", "datetime_last_parsed", "max_requests_per_session", "priority_rate", "is_active", )
    list_filter = ("is_active", "social_network", )
    search_fields = ("name", "query", )


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


# VK
class VKLoginPassAdmin(admin.ModelAdmin):
    list_display = ("login", "app_id", "is_active", "news_feed_limit_used", "wall_get_limit_used", "datetime_created", "datetime_modified", )
    list_filter = ("is_active", )
    search_fields = ("login", "app_id", )


# YouTube
class YouTubeAuthTokenAdmin(admin.ModelAdmin):
    list_display = ("token_id", "is_active", "datetime_created", "datetime_modified", )
    list_filter = ("is_active", )
    search_fields = ("token_id", "is_active", )



# Common
admin.site.register(SocialNetworkAccount, SocialNetworkAccountAdmin)
admin.site.register(MonitoringQuery, MonitoringQueryAdmin)

# Telegram
admin.site.register(TelegramAuthKey, TelegramAuthKeyAdmin)

# Instagram
admin.site.register(InstagramLoginPass, InstagramLoginPassAdmin)

# VK
admin.site.register(VKLoginPass, VKLoginPassAdmin)

# YouTube
admin.site.register(YouTubeAuthToken, YouTubeAuthTokenAdmin)
