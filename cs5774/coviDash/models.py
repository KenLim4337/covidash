from django.db import models
from datetime import datetime

# Create your models here.
class Rumour(models.Model):
    title = models.CharField(max_length=200, default="Rumour Title")
    img = models.CharField(max_length=200, default="/")
    description = models.TextField(default="Description")
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)

    #Rel to user
    #poster = models.OneToOneField('User')
    #Store ID for now
    poster = models.CharField(max_length=200, default="Unknown")

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

class User(models.Model):
    def __init__(self, userId, userName, role, title, password, added, posted, cited, solved): 
        self.userId = userId
        self.userName = userName
        self.role = role
        self.title = title

        #Storing passwords as plaintext because i can
        self.password = password

        #Added rumours
        self.added = added

        #For homepage tally
        self.posted = posted
        self.cited = cited
        self.solved = solved

        #Add other user properties/stats later if needed

        
#Users
users = []

user = User(
    1,
    'Bass',
    'user',
    'Armchair Detective',
    'password',
    [0,1,2,3],
    20,
    12,
    11
)

user2 = User(
    2,
    'Hal',
    'user',
    'Advanced Sleuth',
    'password',
    [2,1,3,4],
    40,
    22,
    5
)

user3 = User(
    3,
    'Mack',
    'user',
    'Novice Investigator',
    'password',
    [5,6,7,3],
    15,
    60,
    1
)

admin = User (
    0,
    'Haddock',
    'admin',
    'Big Cheese',
    'admin',
    [3,4,5,1],
    20,
    12,
    11
)

users.extend([admin, user, user2, user3])