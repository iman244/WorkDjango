from django.db import models
from django.db.models import F, ExpressionWrapper, DurationField
from datetime import timedelta

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
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT, related_name='works')
    description = models.TextField(max_length=4000,default="", blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    overwork_day = models.BooleanField(default=False)

    @property
    def duration(self):
        return self.end - self.start

    @property
    def overwork_duration(self):
        if self.overwork_day:
            return self.end - self.start
        else:
            overwork = self.end - self.start - timedelta(hours=9)   
            return overwork if overwork > timedelta() else timedelta()

    def __str__(self):
        return self.issue.url