from django.contrib import admin
from .models import Issue, Work

class WorkInline(admin.TabularInline):
    model = Work
    extra = 1

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    inlines = [WorkInline]

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    pass
