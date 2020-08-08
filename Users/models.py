from django.db import models

# Create your models here.

class User(models.Model):
    '''
        Class that defines the structure of User objects and also the database table structure of the same.
        defines 3 fields as follows
            id : character field
                unique id of each user
            realname : character field
                real/full name of the user
            tz : character field
                timezone of the user
    '''
    id = models.CharField(max_length=64, primary_key=True)
    realname = models.CharField(max_length=512)
    tz = models.CharField(max_length=64)


class ActivityPeriod(models.Model):
    '''
        Class that defines the structure of Activity objects and also the database table structure of the same.
        defines 4 fields as follows:
            id : integer
                unique id for each activity period
            userid : character field
                the id of user associated with the activity period, forms a foreign key relation with the User table
            starttime - datetime field
                starting time for the activity
            endtime : datetime field
                ending time for the activity
    '''

    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
