# Generated by Django 2.1.4 on 2021-10-12 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_customuser_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='practice',
            name='color',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
