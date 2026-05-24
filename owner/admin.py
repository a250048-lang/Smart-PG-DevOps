from django.contrib import admin
from .models import PGProperty, Room, Booking, User
from .models import Hostel, HostelRule

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1  

@admin.register(PGProperty)
class PGPropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'has_wifi', 'has_food')
    list_filter = ('city', 'has_wifi', 'has_food')
    search_fields = ('name', 'city', 'owner__username')
    inlines = [RoomInline] 

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "district",
        "state",
        "gender",
        "pincode",
        "created_at",
    )

    list_filter = ("gender", "city", "district", "state")

    search_fields = (
        "name",
        "city",
        "district",
        "state",
        "pincode",
    )


