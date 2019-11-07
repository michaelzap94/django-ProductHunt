from django.db import models

#================================================================
#IMPORT THE DJANGO BUILT-IN ADMIN Model 'User'
from django.contrib.auth.models import User
#================================================================

class Product(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500)
    pub_date = models.DateTimeField(auto_now=True)
    votes_total = models.IntegerField(default=1)
    image = models.ImageField(upload_to='images/')  # upload_to='' specify where to upload the image to.
    icon = models.ImageField(upload_to='icons/') # upload_to='' specify where to upload the icon to.
    body = models.TextField()
    # Hunter is an actual User, Stored in the built-in 'User' model provided by Django, 
    # therefore we use .ForeignKey to REFER to the 'id' of this user IN THE User Model.
    # on_delete is REQUIRED, for this on_delete=models.CASCADE --> if the user is deleted, then delete this Product Record.
    hunter = models.ForeignKey(User, on_delete=models.CASCADE) # hunter will contain a User id

    #NAME TO USE WHEN ACCESSING OBJECT(e.g: WHEN DJANGO lists the objects)
    def __str__(self):
        return self.title

    #functions for specific Records in the Table Blog.
    def summary(self):
        return self.body[:100]

    def pub_date_pretty(self):
        return self.pub_date.strftime('%e %b %Y')
    
    def makeUpvote(self):
        self.votes_total = self.votes_total + 1
