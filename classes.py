#GiftMixer project
#R32NOR | anklebiters.
#2024

# file containing class information

import datetime
import tzlocal
import secrets
import string



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
    def __init__(self, userID):
        self.userID = userID
        self.MyGroups = []


    # @classmethod
    # def get_next_ID(cls):
    #     cls.lastID +=1
    #     return cls.lastID

# userTemp = User(userName='', userMail='', userPassword='')

class Group:
    def __init__(self, groupName, adminID):
        self.groupID = ''
        self.groupName = groupName
        self.password = ''.join(secrets.choice(string.digits) for i in range(6))
        self.adminID = adminID
        self.members = []
        self.price_limit = ''
        self.currency = ''
        self.deadline = ''
        self.place = ''
        self.remarks = ''




























