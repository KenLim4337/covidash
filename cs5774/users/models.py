from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from coviDash.models import Rumour

class Details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(default="regular", max_length=50)
    title = models.CharField(default="Amateur Sleuth", max_length=50)

    #Number of rumours added
    posted = models.IntegerField(default=0)
    #Number of citations
    cited = models.IntegerField(default=0)
    #Number of rumours involved in
    solved = models.IntegerField(default=0)

    #Rumours in dashboard
    added = models.ManyToManyField(Rumour)

@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, **kwargs):
        if created:
            Details.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_details(sender, instance, **kwargs):
    instance.details.save()

        