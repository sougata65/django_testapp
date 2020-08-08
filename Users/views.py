from django.shortcuts import render
from Users.serializers import UserSerializer, ActivityPeriodSerializer
from Users.models import User,ActivityPeriod
from sklearn.utils import shuffle

# loading the list of all available user ids in the database in order to send to the front-end
# user_ids = shuffle(list(User.objects.values_list('id', flat=True)), random_state=0)


def index(request):
    '''
    Method for handling requests for the index page ( for the urls '/' and 'index/')
    Renders a page with a list of all the user ids present in the database that the client use to view
    information for individual users and their sessions.

    params:
    -------
    request: HttpRequest
        the request object
    '''
    context = { "user_ids" : user_ids}
    return render(request, 'index.html', context)

def view_user(request, id):
    '''
    Method for handling requests for data of individual users.
    If the user id exists in the database, then the user details and their activity details are retrieved from the database,
    otherwise

    params:
    --------
    request: HttpRequest
        the request object

    id: str
        user id for retrieving data from the database

    '''
    try:
        user = User.objects.get(id=id)
        success = True
    except:
        success = False

    if success:
        user = UserSerializer(user).data
        user_activity_periods = ActivityPeriod.objects.filter(userid=id).order_by('starttime')
        user_activity_periods = ActivityPeriodSerializer(user_activity_periods, many=True).data
        context = {"user": user, "activity_periods": user_activity_periods}

        return render(request, "user.html", context)
    else:
        context = {"message" : f"No user exists with the id {id}."}
        return render(request, 'not_found.html', context)



def not_found(request):
    '''
    Method for handling urls that are lying in the domain but not defined
    Renders a page showing a message that the resource does not exist.

    params:
    --------
    request: HttpRequest
        the request object
    '''
    context = {"message": "The requested url does not exist."}
    return render(request, "not_found.html")
