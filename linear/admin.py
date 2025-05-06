import math
from django.contrib import admin
from .models import Issue, Work
from django.db.models import ExpressionWrapper, F, DurationField, Sum
from django.utils.formats import number_format
from datetime import timedelta
from .actions import mark_as_overwork
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget


class WorkInline(admin.TabularInline):
    model = Work
    extra = 1

@admin.register(Issue)
class IssueAdmin(ImportExportModelAdmin):
    list_display = ('url', 'duration')
    inlines = [WorkInline]
    formats = [base_formats.CSV, base_formats.XLSX]

    def changelist_view(self, request, extra_context=None):
        # Call the superclass to get the default context
        response = super().changelist_view(request, extra_context=extra_context)
        
        # Get the ChangeList object to access the filtered queryset
        try:
            cl = response.context_data.get('cl')
            if cl:
               # Annotate each Issue with its total duration
                queryset = cl.queryset.annotate(
                    total_duration=ExpressionWrapper(
                        Sum(F('works__end') - F('works__start')),
                        output_field=DurationField()
                    )
                )

                # Aggregate the total duration across all Issues
                total_duration = queryset.aggregate(
                    total_duration_sum=Sum('total_duration')
                )['total_duration_sum'] or timedelta()

                # Format the total duration as a string
                total_seconds = int(total_duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_total = f"{hours}h {minutes}m"
                
                total_overwork = timedelta()
                for i in queryset.all():
                    for work in i.works.all():
                        total_overwork += work.overwork_duration
                    # print("work", work.start)

                # Format the total overwork duration as a string
                ow_total_seconds = int(total_overwork.total_seconds())
                ow_hours, ow_remainder = divmod(ow_total_seconds, 3600)
                ow_minutes, ow_seconds = divmod(ow_remainder, 60)
                ow_formatted_total = f"{ow_hours}h {ow_minutes}m"
                    
                # Add the total to the template context
                response.context_data['total'] = formatted_total
                response.context_data['total_overwork'] = ow_formatted_total
                p = 250 * 10 ** 3
                response.context_data['total_value'] = f"{(math.floor(((hours + minutes / 60 ) * p) + (ow_hours + ow_minutes / 60 ) * p * 0.4)):,}"

            return response
        except:
            return response


class WorkResource(resources.ModelResource):
    issue = fields.Field(
        column_name='issue',
        attribute='issue',
        widget=ForeignKeyWidget(Issue, 'url')  # or another identifying field
    )
    duration = fields.Field()
    overwork_duration = fields.Field()

    class Meta:
        model = Work
        fields = ('issue', 'start', 'end', 'duration', 'overwork_duration')
        export_order = ('issue', 'start', 'end', 'overwork_duration', 'duration')

    def dehydrate_duration(self, obj):
        return obj.duration

    def dehydrate_overwork_duration(self, obj):
        return obj.overwork_duration

@admin.register(Work)
class WorkAdmin(ImportExportModelAdmin):
    list_display = ('issue', 'wage_month', 'start', 'end', 'overwork_duration', 'duration')
    list_filter = ('wage_month',)
    actions = [mark_as_overwork]
    formats = [base_formats.CSV, base_formats.XLSX]
    resource_class = WorkResource

    def changelist_view(self, request, extra_context=None):
        # Call the superclass to get the default context
        response = super().changelist_view(request, extra_context=extra_context)
        
        # Get the ChangeList object to access the filtered queryset
        try:
            cl = response.context_data.get('cl')
            if cl:
               # Annotate each Issue with its total duration
                queryset = cl.queryset.annotate(
                    total_duration=ExpressionWrapper(
                        Sum(F('end') - F('start')),
                        output_field=DurationField()
                    )
                )

                # Aggregate the total duration across all Issues
                total_duration = queryset.aggregate(
                    total_duration_sum=Sum('total_duration')
                )['total_duration_sum'] or timedelta()

                # Format the total duration as a string
                total_seconds = int(total_duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_total = f"{hours}h {minutes}m"
                
                total_overwork = timedelta()
                for work in queryset:
                    total_overwork += work.overwork_duration
                    # print("work", work.start)

                # Format the total overwork duration as a string
                ow_total_seconds = int(total_overwork.total_seconds())
                ow_hours, ow_remainder = divmod(ow_total_seconds, 3600)
                ow_minutes, ow_seconds = divmod(ow_remainder, 60)
                ow_formatted_total = f"{ow_hours}h {ow_minutes}m"
                    
                # Add the total to the template context
                response.context_data['total'] = formatted_total
                response.context_data['total_overwork'] = ow_formatted_total
                p = 250 * 10 ** 3
                response.context_data['total_value'] = f"{(math.floor(((hours + minutes / 60 ) * p) + (ow_hours + ow_minutes / 60 ) * p * 0.4)):,}"
                            
            return response
        except:
            return response