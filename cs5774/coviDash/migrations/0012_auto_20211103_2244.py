# Generated by Django 3.1.4 on 2021-11-04 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coviDash', '0011_auto_20211103_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='rumour',
            name='versource',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='rumour',
            name='verusers',
            field=models.IntegerField(default=0),
        ),
    ]
