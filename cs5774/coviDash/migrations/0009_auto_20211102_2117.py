# Generated by Django 3.1.4 on 2021-11-03 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coviDash', '0008_auto_20211102_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rumour',
            name='poster',
            field=models.CharField(default='Unknown', max_length=200),
        ),
    ]
