# Generated by Django 3.1.4 on 2021-11-13 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coviDash', '0013_auto_20211113_1653'),
        ('users', '0003_details_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='details',
            name='added',
            field=models.ManyToManyField(to='coviDash.Rumour'),
        ),
    ]
