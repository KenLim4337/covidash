# Generated by Django 3.1.4 on 2021-11-17 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coviDash', '0020_comment_edited'),
    ]

    operations = [
        migrations.AddField(
            model_name='rumour',
            name='edited',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
