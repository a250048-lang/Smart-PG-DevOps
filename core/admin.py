from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'rating', 'is_approved', 'created_at')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('name', 'email', 'message')