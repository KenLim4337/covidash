from django.db import models

# Create your models here.
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

        