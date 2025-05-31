from django.contrib import admin
from .models import Event, Photo

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_code', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active', 'start_time')
    search_fields = ('name', 'event_code')
    list_editable = ('is_active',)
    list_per_page = 20

    prepopulated_fields = {'event_code': ('name',)}

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('image', 'event', 'uploaded_by', 'uploaded_at')
    list_filter = ('event', 'uploaded_at', 'uploaded_by')
    search_fields = ('description', 'event__name', 'uploaded_by__email')
    raw_id_fields = ('event', 'uploaded_by')


