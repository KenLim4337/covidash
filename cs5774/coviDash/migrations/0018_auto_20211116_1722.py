# Generated by Django 3.1.4 on 2021-11-16 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coviDash', '0017_auto_20211116_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='validity',
            field=models.IntegerField(default='0'),
        ),
    ]
