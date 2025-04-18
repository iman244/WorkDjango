from django.contrib import admin
from .models import Work

@admin.action(description="Mark selected works as overwork")
def mark_as_overwork(modeladmin, request, queryset):
    queryset.update(overwork_day=True)