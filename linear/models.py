from django.db import models
from django.db.models import F, ExpressionWrapper, DurationField
from datetime import timedelta

# Create your models here.
class Issue(models.Model):
    url = models.URLField()
    description = models.TextField(max_length=4000)


    def duration(self):
        """
        Calculate the total duration of all related Work instances.
        """
        # Query related Work objects and annotate their durations
        total_duration = self.works.annotate(
            duration=ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
        ).aggregate(total_duration=models.Sum('duration'))['total_duration']

        return total_duration or timedelta()
        # for work in self.works.all():
        #      print(work.duration())

        # return sum(work.duration() for work in self.works.all())

    def __str__(self):
        return self.url


class Work(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT, related_name='works')
    start = models.DateTimeField()
    end = models.DateTimeField()

    def duration(self):
        return self.end - self.start

    def __str__(self):
        return self.issue.url