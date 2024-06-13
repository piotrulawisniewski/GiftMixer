#GiftMixer project
#R32NOR | anklebiters.
#2024

### FUNCTIONS ###
# all general functions

# libs & modules

import datetime
import tzlocal
import random

# Local time Timestamp function for quick get current time for saving
def py_local_timestamp():
    """FUNCTION: use to return local time timestamp
       :param
       :return local timestamp
       """
    local_timezone = tzlocal.get_localzone()
    local_timestamp = datetime.datetime.now(local_timezone)
    return local_timestamp

# UTC time Timestamp function for quick get current UTC time for saving
def py_utc_timestamp():
    """FUNCTION: use to return UTC time timestamp
           :param
           :return utc timestamp
           """
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc)
    return utc_timestamp


def simple_passwd():

    print('12345678: this function will be changed')














