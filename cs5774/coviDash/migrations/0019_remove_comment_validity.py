# Generated by Django 3.1.4 on 2021-11-16 23:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coviDash', '0018_auto_20211116_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='validity',
        ),
    ]
