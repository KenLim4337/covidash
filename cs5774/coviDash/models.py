from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.
class Rumour(models.Model):
    title = models.CharField(max_length=200, default="Rumour Title")
    img = models.CharField(max_length=200, default="/")
    description = models.TextField(default="Description")
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)

    #Rel to user
    poster = models.ForeignKey(User, on_delete=models.CASCADE)

    #Verification stats and things mostly votes
    verusersF = models.IntegerField(default=0)
    verusersT = models.IntegerField(default=0)

    #Sum of the two
    verusers = models.IntegerField(default=0)

    #Will be replaced by foreign keys
    versourceF = models.IntegerField(default=0)
    versourceT = models.IntegerField(default=0)
    #Sum of the two
    versource = models.IntegerField(default=0)

    validity = models.CharField(max_length=200, default="Mixed")

    #Big text properties
    bodyHtml = models.TextField(default="HTML Body")
    citation = models.TextField(null=True)

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    rumour = models.ForeignKey(Rumour, on_delete=models.CASCADE)
    body = models.TextField(default="Comment Body")
    validity = models.CharField(max_length=200, default="False")
    score = models.IntegerField(default=0)


class Source(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    rumour = models.ForeignKey(Rumour, on_delete=models.CASCADE)
    url = models.TextField(max_length=200)    
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    validity = models.CharField(max_length=200, default="False")