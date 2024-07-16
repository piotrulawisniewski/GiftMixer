#GiftMixer project
#R32NOR | anklebyters.
#2024

### FUNCTIONS ###
# all general purpose functions

# libs & modules

import datetime as dt
import tzlocal
from datetime import datetime
import pytz


local_timezone = tzlocal.get_localzone()




# Local time Timestamp function for quick get current time for saving
def py_local_timestamp():
    """FUNCTION: use to return local time timestamp
       :param
       :return local timestamp
       """
    local_timezone = tzlocal.get_localzone()
    local_timestamp = datetime.now(local_timezone)
    return local_timestamp

# UTC time Timestamp function for quick get current UTC time for saving
def py_utc_timestamp():
    """FUNCTION: use to return UTC time timestamp
           :param
           :return utc timestamp
           """
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc)
    return utc_timestamp




################################################################################

'''

def get_offset_aware_datetime(user_input, timezone_str='UTC'):
    """
    Converts a user input string into an offset-aware datetime object.

    Parameters:
        user_input (str): The datetime string provided by the user.
        timezone_str (str): The timezone to use (default is 'UTC').

    Returns:
        datetime: An offset-aware datetime object.
    """
    # Define the timezone
    timezone = pytz.timezone(timezone_str)

    # Try to parse the input in different formats
    try:
        if len(user_input) == 10:  # Format YYYY-MM-DD
            naive_dt = datetime.strptime(user_input, "%Y-%m-%d")
            naive_dt = naive_dt.replace(hour=0, minute=0)
        elif len(user_input) == 16:  # Format YYYY-MM-DD HH:mm
            naive_dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
        else:
            raise ValueError("Input format is not correct")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")

    # Localize the naive datetime to the specified timezone
    aware_dt = timezone.localize(naive_dt)
    return aware_dt


# Example usage
user_input_1 = "2024-07-09"
user_input_2 = "2024-07-09 15:30"
# timezone_str = 'America/New_York'
timezone_str = str(local_timezone)



print(get_offset_aware_datetime(user_input_1, timezone_str))
print(get_offset_aware_datetime(user_input_2, timezone_str))
# print(get_offset_aware_datetime(user_input_2, local_timezone))


local_timezone = tzlocal.get_localzone()
print(local_timezone)
print(type(local_timezone))
timezone = pytz.timezone(timezone_str)

print(timezone)
print(type(timezone))



timezone1 = dt.timezone(offset=dt.timedelta(hours=-2))
print(timezone1)






'''


