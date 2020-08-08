from django.core.management.base import BaseCommand
from Users.models import User, ActivityPeriod
from numpy.random import randint
import pandas as pd
from baseconvert import base
from datetime import timedelta
from randomtimestamp import randomtimestamp
from functools import reduce
from pytz import timezone as get_timezone
from tqdm import tqdm, trange
import string

## just a function, which is not directly related to our case
def get_conversion_dict():
    '''
        creates a dictionary mapping numbers to letters and digits
        all the digits and alphabets will be mapped to a numbers between 0 and 61
        it will be for converting integer ids to a string id
        will return a dictionary that looks like the following:
            {0 : '0', 1 : '1', ..., 9:'9', 10: 'a', 11: 'b', ..., 60: 'Y', 61: 'Z'}
    '''
    digits = string.digits
    conversion_dict = { i:digits[i] for i in range(len(digits))}
    letters = string.ascii_letters
    conversion_dict = { **conversion_dict, **dict(zip(range(len(digits), len(digits) + len(letters)), letters))}
    return conversion_dict

conversion_dict = get_conversion_dict()


def integer_id_to_string_id(integer_id):
    '''
        converts an integer to a base 62 number and maps the individual digits to a alphanumeric character with the
        help of the conversion dict created above

        this function and the get_conversion dict function are just for making string ids out of integer ids and might not
        be crucial to our case unless string ids are compulsory
    '''
    return "".join([conversion_dict[digit] for digit in base(integer_id, 10, 62)])


class Command(BaseCommand):
    '''
        Class for creating a command which can be used from the terminal to populate database with generated data
    '''
    help = 'Populate database with sample data'

    def add_arguments(self, parser):
        '''
            adds arguments to the command to determine variables for populating data
        '''

        #   number of user records to be inserted into the database
        parser.add_argument('--no-user-records', type=int)

        #   number of activity period entries to be inserted into the database per user, within the range entered
        parser.add_argument('--no-periods-per-user', nargs=2, type=int)

        #   argument for localizing datetimes according to user timezones (making them timzezone 'aware' instead of 'naive')
        parser.add_argument('--localize-datetime', default=False)

    def handle(self, *args, **options):
        '''
            this method populates the database with randomly generated values with the help of other functions in this module
        '''

        ## receiving command line arguments
        no_of_users_records = options["no_user_records"]
        min_periods_per_user, max_periods_per_user = options['no_periods_per_user']
        use_user_timezone = options['localize_datetime'].lower() == 'true'
        assert min_periods_per_user<=max_periods_per_user

        ## reading sample data for names and timezones in order to generate new samples from them
        with open('Users/datapopulation/first_names_all.txt', 'r') as file:
            first_names = file.read().split("\n")
        with open('Users/datapopulation/last_names_all.txt', 'r') as file:
            last_names = file.read().split("\n")
        timezones = list(pd.read_csv("Users/datapopulation/zone.csv", header=None)[2])

        ## calling the other functions defined and populating the database
        self.populate_database(no_of_users_records, min_periods_per_user, max_periods_per_user, first_names, last_names, timezones, use_user_timezone=use_user_timezone)



    # generate a single User instance with randomly selected values
    def generate_single_user_instance(self, serial_no, first_names, last_names, timezones, no_of_first_names, no_of_last_names, no_of_timezones):
        '''
            description : generates a User object by combining first and last names to a realname field, choosing a random timezone
                            and using the id passed.


            params
            ------
            serial_no : int
                the id of the user generated as a serial (increment by one) which is to be converted to a string_id using
                the integer_id_to_string_id method
            first_names : list
                a list containing common first names of people
            last_names : list
                a list containing common last names of people
            timezones : list
                a list containing names of different timezones around the world
            no_of_first_names : int
                number of first names in the first_names list, equals len(first_names)
            no_of_first_names : int
                number of last names in the last_names list, equals len(last_names)
            no_of_first_names : int
                number of timezones in the timezones list, equals len(timezones)

            returns
            -------
            A models.User object
        '''
        realname = " ".join([first_names[randint(0, no_of_first_names)], last_names[randint(0,no_of_last_names)]])
        realname = realname.title()
        timezone = timezones[randint(0,no_of_timezones)]
        return User(id=integer_id_to_string_id(serial_no), realname = realname, tz = timezone )

    # create User instances for populating database
    def create_user_instances(self, no_of_instances, first_names, last_names, timezones, id_offset=int(1e20)):
        '''
            description : generates the number of User instances specified in the no_of_instances_variable

            params
            ------
            no_of_instances : int
                the number of objects to be created and returned
            first_names : list
                a list containing common first names of people
            last_names : list
                a list containing common last names of people
            timezones : list
                a list containing names of different timezones around the world
            id_offset : int
                a large number, the minimum integer id is this number and is incremented by 1 for each new object to be generated
                has no real purpose other than to making the length of the string id large

            returns
            -------
            A list of models.User objects
        '''
        no_of_first_names = len(first_names)
        no_of_last_names = len(last_names)
        no_of_timezones = len(timezones)
        print(f"Creating dummy data for {no_of_instances} users...")
        instances = [ self.generate_single_user_instance(serial_no, first_names, last_names, timezones, no_of_first_names, no_of_last_names, no_of_timezones) for serial_no in trange(id_offset, id_offset+no_of_instances)]
        return instances

    # method for creating a single ActivityPeriod instance
    def create_activity_period_single_instance(self, user, min_minutes_per_session, max_minutes_per_session, starting_year, user_timezone = None):
        '''
            description : creates a single instance of models.ActivityPeriod for the particular user

            params
            -------
            user : models.User
                the user id for which the ActivityPeriod has to be created is retrieved from this User object
            min_minutes_per_session : int
                the minimum number of minutes that an ActivityPeriod will have i.e. endtime - starttime >= min_minutes_per_session
            max_minutes_per_session : int
                the maximum number of minutes that an ActivityPeriod will have i.e. endtime - starttime <= max_minutes_per_session
            starting_year : int
                year after which datetimes will be generated e.g. if starting year is 2010, all dates generated will
                be after 2010
            user_timezone : str
                the timezone of the user. if None the datetimes generated will be naive

            returns
            -------
            An instance of models.ActivityPeriod

        '''

        # generate a random timestamp after starting year which will be our starttime and add a value within the range
        # (min_minutes_per_session, max_minutes_per_session) to obtain a random endtime
        start_datetime = randomtimestamp(starting_year, False)
        end_datetime = start_datetime + timedelta(minutes=randint(min_minutes_per_session, max_minutes_per_session))

        # if user_timezone is passed convert the datetime to a timezone localized datetime
        if user_timezone:
            user_timezone = get_timezone(user_timezone)
            start_datetime = user_timezone.localize(start_datetime)
            end_datetime = user_timezone.localize(end_datetime)

        return ActivityPeriod(userid=user, starttime=start_datetime, endtime=end_datetime)

    # method for creating multiple ActivityPeriod instances for a single user
    def create_activity_period_instances_for_single_user(self, user,
                                                         no_of_periods, min_minutes_per_session = 0.2, max_minutes_per_session=1000,
                                                         starting_year= 2010, user_timezone = None):
        '''
            description : for a single users, generates multiple activity periods specified by the no_of_periods

            params
            ------
            user : models.User
                the user id for which the ActivityPeriod has to be created is retrieved from this User object
            no_of_periods : int
                the number of instances to be generated for the given user
            min_minutes_per_session : int
                the minimum number of minutes that an ActivityPeriod will have i.e. endtime - starttime >= min_minutes_per_session
            max_minutes_per_session : int
                the maximum number of minutes that an ActivityPeriod will have i.e. endtime - starttime <= max_minutes_per_session
            starting_year : int
                year after which datetimes will be generated e.g. if starting year is 2010, all dates generated will
                be after 2010
            user_timezone : str
                the timezone of the user. if None the datetimes generated will be naive

            returns
            -------
            A list of models.ActivityPeriod objects with the same userid
        '''
        return [ self.create_activity_period_single_instance(user, min_minutes_per_session, max_minutes_per_session, starting_year, user_timezone) for i in range(no_of_periods)]

    # method for generating activity periods of users from a list of user ids
    def create_activity_periods_for_all_users(self, users, min_periods = 1, max_periods = 16, use_user_timezone = True):
        '''
            description : creates several activity periods individually for all the users given

            params
            ------
            users : list
                a list of models.User instances, whose ids are to be used to creating ActivityPeriod instances
            min_periods : int
                the minimum number of activity periods to be generated per user
            max_periods : int
                the minimum number of activity periods to be generated per user
            use_user_timezone : boolean
                if true, gets the timezone from the User objects and localizes the datetimes (starttime and endtime) in the
                ActivityPeriod instances to be generated

            returns
            -------
            a list of models.ActivityPeriod instances
        '''
        print(f"Creating dummy data for activity periods for {len(users)} users...")

        # get an individual list of ActivityPeriod instances for each user and store them in a single list
        if use_user_timezone:
            results = [ self.create_activity_period_instances_for_single_user(user, randint(min_periods, max_periods), user_timezone=user.tz) for user in tqdm(users)]
        else:
            results = [ self.create_activity_period_instances_for_single_user(user, randint(min_periods, max_periods), user_timezone=None) for user in tqdm(users)]
        print("Reducing results to single list...")
        # reduce the nested list structure into a single list of ActivityPeriod instances
        results = reduce(lambda x,y : [*x,*y], tqdm(results))
        return results

    # method for populating both the users and activity period database using the methods described above
    def populate_database(self, no_of_users_records, min_periods_per_user, max_periods_per_user, first_names, last_names, timezones, use_user_timezone=False):
        '''
            description : generates a list of users and a list of activity periods for the users, and stores them in the database

            params
            ------
            no_of_user_records : int
                the number of User instances to be generated
            min_periods_per_user : int
                the minimum number of activity periods to be generated per user
            max_periods_per_user : int
                the minimum number of activity periods to be generated per user
            first_names : list
                a list containing common first names of people
            last_names : list
                a list containing common last names of people
            timezones : list
                a list containing names of different timezones around the world
            use_user_timezone : boolean
                whether to localize datetime entities with the user's timezone
        '''
        users_data = self.create_user_instances(no_of_users_records, first_names, last_names, timezones)
        acitivity_periods_data = self.create_activity_periods_for_all_users([ user for user in users_data], use_user_timezone=use_user_timezone)
        print("Dummy data created.")

        print("Populating users data...")
        User.objects.bulk_create(users_data)
        print("Users data populated successfully.")

        print("Populating activity periods data...")
        ActivityPeriod.objects.bulk_create(acitivity_periods_data)
        print("Activity periods data populated successfully.")
