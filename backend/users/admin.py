from django.contrib import admin
from django.contrib.auth.models import User

from .models import Follow


class UserAdmin(admin.ModelAdmin):
    """Admin interface for user accounts."""
    list_display: tuple = ("email", "first_name", "last_name")
    list_filter: tuple = ("username", "email")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin interface for user subscriptions."""
    list_display: tuple = ("user", "author")
    empty_value_display: tuple = "пусто"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
