#GiftMixer project
#R32NOR | ZOLCBYTERS
#2024

# file containing class information

import datetime
import tzlocal
import secrets
import string
from collections import OrderedDict    # module to ensure the order of class keys


import database

#connection to database
if __name__ == "__main__":
    db_connection = database.db_switch_on()
    cursor = db_connection.cursor()

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

class Group:
    def __init__(self,groupName, adminID):

        self.groupID = ''
        self.groupName = groupName
        self.PIN = ''.join(secrets.choice(string.digits) for i in range(6))
        self.adminID = adminID
        self.members = []
        self.price_limit = ''
        self.place = ''
        self.meetingDate = ''
        self.deadline = ''
        self.remarks = ''
        self.usersFinished = 0

class Gift:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Giver_data():
    def __init__(self, giverID, mail = None, nick = None, receiverName = None, groupName = None, wishlist_to_buy = None):
        self.ID = giverID
        self.mail = mail
        self.nick = nick
        self.receiverName = receiverName
        self.groupName = groupName
        self.wishlist = wishlist_to_buy

    def to_ordered_dict(self):
        return OrderedDict([
            ("ID", self.ID),
            ("mail", self.mail),
            ("nick", self.nick),
            ("receiverName", self.receiverName),
            ("groupName", self.groupName),
            ("whishlist", self.wishlist)
        ])















































