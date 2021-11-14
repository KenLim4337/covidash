from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import tree
from coviDash.models import Rumour, Comment, Source, Vote

verbdict = {
    "RC": "commented on a rumour",
    "AS": "added a source to a rumour",
    "RV": "voted",
    "AR": "added a rumour",
    "RE": "edited a rumour"
}

class Action(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #Rumour Comment: commented on a rumour, Add Source: added a source to a rumour, Rumour Vote: voted on a rumour, Add Rumour: added a rumour, Rumour Edit: edited a rumour
    verb = models.CharField(max_length=100)
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name='target_obj', on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')
    #Date done
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)

    def get_verb(self): 
        return verbdict.get(self.verb)

