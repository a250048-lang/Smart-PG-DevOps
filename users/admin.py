from django.contrib import admin
from .models import TenantProfile, OwnerProfile


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile_number")


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile_number", "kyc_status")
