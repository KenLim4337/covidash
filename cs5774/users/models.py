from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ManyToManyField
from django.db.models.signals import post_save
from django.dispatch import receiver
from coviDash.models import Rumour, Comment, Source
from actions.models import Action
from django.urls import reverse

#0 = Admin
titleList = ['Chief Gumshoe', 'Amateur Snooper', 'Novice Investigator', 'Intermediate Detective', 'Expert Inspector', 'Master Sleuth']

class Details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(default="regular", max_length=50)
    level = models.PositiveIntegerField(default=1)
    subscribed = ManyToManyField(Rumour)

    def get_absolute_url(self):
        return reverse('users:profile', args=[self.user.username.lower()])

    def make_admin(self): 
        self.role = "admin"
        self.level = 0
        self.save()

    def strip_admin(self): 
        self.role = "regular"
        if int(Action.objects.filter(user = self.user).count()/10) + 1 < 5:
            self.level = int(Action.objects.filter(user = self.user).count()/10) + 1
        else: 
            self.level = 5
        self.save()
        
    def check_level(self):
        if self.role == "regular":
            if self.level != int(Action.objects.filter(user = self.user).count()/10) + 1 and self.level < 5:
                self.level = int(Action.objects.filter(user = self.user).count()/10) + 1
                self.save()

                activityLog = Action(
                    user = self.user,
                    verb = "CT"
                )

                activityLog.save()


    def get_title(self):
        return titleList[self.level]

    def get_name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def get_posted(self):
        return Rumour.objects.filter(poster = self.user).count()
    
    def get_cited(self):
        return Source.objects.filter(commenter = self.user).count()

    def get_solved(self):
        return Comment.objects.filter(commenter = self.user).values('rumour').distinct().count()


@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, **kwargs):
    if kwargs['raw']:
        return

    if created:
        Details.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_details(sender, instance, **kwargs):
    if kwargs['raw']:
        return
        
    instance.details.save()

        