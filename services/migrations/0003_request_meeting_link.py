# Generated by Django 2.1.4 on 2021-10-12 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_request_declined'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='meeting_link',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
