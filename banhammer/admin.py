from django.contrib import admin

from .models import AccountSettings, BanableUser, BanableUserVariant, BanHammer


@admin.register(AccountSettings)
class AccountSettingsModelAdmin(admin.ModelAdmin):
    pass


@admin.register(BanHammer)
class BanHammer(admin.ModelAdmin):
    pass


class BanableUserVariaqntInline(admin.TabularInline):
    model = BanableUserVariant


@admin.register(BanableUser)
class BanableUserModelAdmin(admin.ModelAdmin):
    inlines = [
        BanableUserVariaqntInline,
    ]

