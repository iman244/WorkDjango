# Generated by Django 5.1.7 on 2025-03-24 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linear', '0002_alter_work_issue'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='description',
        ),
        migrations.AddField(
            model_name='work',
            name='description',
            field=models.TextField(blank=True, default='', max_length=4000, null=True),
        ),
    ]
