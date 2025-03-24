from django.contrib import admin
from .models import Issue, Work
from django.db.models import ExpressionWrapper, F, DurationField, Sum
from django.utils.formats import number_format
from datetime import timedelta


class WorkInline(admin.TabularInline):
    model = Work
    extra = 1

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('url', 'duration')
    inlines = [WorkInline]
    
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
                formatted_total = f"{hours}h {minutes}m {seconds}s"

                # Add the total to the template context
                response.context_data['total'] = formatted_total
            
            return response
        except:
            return response


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('issue', 'start', 'end', 'duration')

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
                formatted_total = f"{hours}h {minutes}m {seconds}s"

                # Add the total to the template context
                response.context_data['total'] = formatted_total
            
            return response
        except:
            return response