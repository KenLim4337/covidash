from django.db import models
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Sum

upvote_to_text = {
    '-1': 'False',
    '1': 'True'
}

truth_html = {
    '-1': '<span class="cross"></span><span>False</span>',
    '0': '<span class="mixed"></span><span>Mixed</span>',
    '1': '<span class="tick"></span><span>True</span>'
}

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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('coviDash:rumour-detail', args=[self.id])

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    rumour = models.ForeignKey(Rumour, on_delete=models.CASCADE)
    body = models.TextField(default="Comment Body")
    #+1, 0 or -1
    validity = models.IntegerField(default="0")
    #Date posted
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)

    def __str__(self):
        return self.rumour.title

    def get_updoots(self):
        updoots = Updoots.objects.filter(comment = self).aggregate(Sum('validity')).get('validity__sum')

        if updoots == None:
            updoots = 0

        return updoots
    
    def validity_html(self):
        return truth_html[self.validity]

class Updoots(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    #+1 or -1
    validity = models.IntegerField(default="0")

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    rumour = models.ForeignKey(Rumour, on_delete=models.CASCADE)
    validity = models.CharField(max_length=200, default="False")

    def __str__(self):
        return "<span>" + (upvote_to_text[self.validity] + " on the rumour: </span>" + self.rumour.title)

    def get_absolute_url(self):
        return reverse('coviDash:rumour-detail', args=[self.rumour.id])

class Source(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    rumour = models.ForeignKey(Rumour, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="Source Title")
    url = models.TextField(max_length=200)    
    #Source Date
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    validity = models.CharField(max_length=200, default="False")

    def __str__(self):
        return self.title