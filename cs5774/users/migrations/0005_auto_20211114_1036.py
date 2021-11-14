# Generated by Django 3.1.4 on 2021-11-14 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coviDash', '0014_comment_source_vote'),
        ('users', '0004_auto_20211113_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='details',
            name='updoots',
            field=models.ManyToManyField(to='coviDash.Comment'),
        ),
        migrations.AddField(
            model_name='details',
            name='voted',
            field=models.ManyToManyField(related_name='vote_relation', to='coviDash.Rumour'),
        ),
        migrations.AlterField(
            model_name='details',
            name='added',
            field=models.ManyToManyField(related_name='add_relation', to='coviDash.Rumour'),
        ),
    ]
