from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import Subscriptions

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar_tag'
    )
    search_fields = ('email', 'username')
    list_display_links = ('email',)
    ordering = ('date_joined',)
    BaseUserAdmin.fieldsets += (
        ('Extra Fields', {'fields': ('avatar',)}),
    )

    def avatar_tag(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50"/>'.format(obj.avatar.url)
            )

    avatar_tag.short_description = 'Аватар'


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
