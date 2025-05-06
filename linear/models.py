from django.db import models
from django.db.models import F, ExpressionWrapper, DurationField
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Issue(models.Model):
    url = models.URLField()

    def duration(self):
        """
        Calculate the total duration of all related Work instances.
        """
        # Query related Work objects and annotate their durations
        total_duration = self.works.annotate(
            duration=ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
        ).aggregate(total_duration=models.Sum('duration'))['total_duration']

        return total_duration or timedelta()

    def __str__(self):
        return self.url


class Work(models.Model):
    PERSIAN_MONTHS = (
        ('فروردین', 'فروردین'),
        ('اردیبهشت', 'اردیبهشت'),
        ('خرداد', 'خرداد'),
        ('تیر', 'تیر'),
        ('مرداد', 'مرداد'),
        ('شهریور', 'شهریور'),
        ('مهر', 'مهر'),
        ('آبان', 'آبان'),
        ('آذر', 'آذر'),
        ('دی', 'دی'),
        ('بهمن', 'بهمن'),
        ('اسفند', 'اسفند'),
    )
    
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT, related_name='works')
    description = models.TextField(max_length=4000,default="", blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    overwork_day = models.BooleanField(default=False)
    wage_month = models.CharField(_("wage month"), max_length=2550, choices=PERSIAN_MONTHS, blank=True, null=True, default='فروردین')

    @property
    def duration(self):
        return self.end - self.start

    @property
    def overwork_duration(self):
        if self.overwork_day:
            return self.end - self.start
        else:
            # Get all works from same day
            same_day_works = Work.objects.filter(
                start__date=self.start.date(),
                end__date=self.end.date()
            ).order_by('start')
            
            # Calculate total duration for the day
            total_duration = timedelta()
            for work in same_day_works:
                total_duration += work.end - work.start
            
            # If total duration is less than 9 hours, no overwork
            if total_duration <= timedelta(hours=9):
                return timedelta()
            
            # Calculate when the 9-hour mark is passed
            nine_hour_mark = None
            running_total = timedelta()
            for work in same_day_works:
                work_duration = work.end - work.start
                if running_total + work_duration > timedelta(hours=9):
                    # This is the work where 9-hour mark is passed
                    nine_hour_mark = work.start + (timedelta(hours=9) - running_total)
                    break
                running_total += work_duration
            
            # If this work starts after the 9-hour mark, it's all overwork
            if self.start >= nine_hour_mark:
                return self.end - self.start
            
            # If this work spans the 9-hour mark
            if self.start < nine_hour_mark and self.end > nine_hour_mark:
                return self.end - nine_hour_mark
            
            # If this work is entirely before the 9-hour mark
            return timedelta()

    def __str__(self):
        return self.issue.url