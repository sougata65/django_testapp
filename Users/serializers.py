from Users.models import User, ActivityPeriod
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    '''
        class for serializing instances of models.User
    '''
    class Meta:
        '''
            class which contains the information for which target class and it's fields to be serialized.
            all fields (id, realname, tz or timezone) are selected as required.
        '''
        model = User
        fields = "__all__"



class ActivityPeriodSerializer(serializers.ModelSerializer):
    '''
        Class for serializing instances of models.ActivityPeriod model
    '''
    class Meta:
        '''
            class which contains the information for which target class and it's fields to be serialized.
            fields selected are startime and endtime as required.
        '''
        model = ActivityPeriod
        fields = ["starttime", "endtime"]

    def to_representation(self, instance):
        '''
            Method for changing the format of datetime values (starttime and endtime) of an instance of models.ActivityPeriod
            as required. Reformats the datetime to the format "%b %d %Y %X%p" --> e.g - Sep 21 2010 21:55:28PM
        '''
        representation = super(ActivityPeriodSerializer, self).to_representation(instance)
        representation['starttime'] = instance.starttime.strftime("%b %d %Y %X%p")
        representation['endtime'] = instance.endtime.strftime("%b %d %Y %X%p")
        return representation
