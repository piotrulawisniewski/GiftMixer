#GiftMixer project
#R32NOR | bilebyters.
#2024

# file containing class information

import datetime
import tzlocal
import secrets
import string


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


class User_Mail_Data:
    def __init__(self, userID, nick, userMail, wishlist_to_buy):
        self.ID = userID
        self.nick = nick
        self.mail = userMail
        self.wishlist = wishlist_to_buy





# class Many_Mails:
#     def __init__(self, recipients_list, ):
#         self.recipients = recipients_list
































