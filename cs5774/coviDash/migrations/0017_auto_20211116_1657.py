# Generated by Django 3.1.4 on 2021-11-16 21:57

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coviDash', '0016_commentvote'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CommentVote',
            new_name='Updoots',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='score',
        ),
    ]
