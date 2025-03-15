from django.db import models

# Create your models here.
class Issue(models.Model):
    url = models.URLField()
    description = models.TextField(max_length=4000)

    def __str__(self):
        return self.url


class Work(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.issue.url