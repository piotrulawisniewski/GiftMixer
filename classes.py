#GiftMixer project
#R32NOR|anklebiters
#2024

# file containing class information

import datetime
import tzlocal

# time variables for time stamping

local_timezone = tzlocal.get_localzone()
local_timestamp = datetime.datetime.now(local_timezone)
utc_timestamp = datetime.datetime.now(datetime.timezone.utc)
local_timestamp_display = local_timestamp.strftime("%Y-%m-%d %H:%M:%S")
utc_timestamp_display = utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")

# print(local_timezone)
# print(local_timestamp)
# print(utc_timestamp)
# print(local_timestamp_display)
# print(utc_timestamp_display)


class User:
    # lastID = 100000000  # ID's will be 100000000+
    def __init__(self, userMail, userPassword):
        self.userID = ''
        self.userName = ''
        self.userMail = userMail
        self.userPassword = userPassword
        self.localTimeStamp = local_timestamp
        self.utcTimeStamp = utc_timestamp


    # @classmethod
    # def get_next_ID(cls):
    #     cls.lastID +=1
    #     return cls.lastID

# userTemp = User(userName='', userMail='', userPassword='')




















