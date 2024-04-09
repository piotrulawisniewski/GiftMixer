#GiftMixer project
#R32NOR|anklebiters
#2024

# file containing class information

import datetime

localTimeStamp = datetime.datetime.now()
utcTimeStamp = datetime.datetime.now(datetime.timezone.utc)
localTimeStamp_display = localTimeStamp.strftime("%Y-%m-%d %H:%M:%S")
utcTimeStamp_display = utcTimeStamp.strftime("%Y-%m-%d %H:%M:%S")



class User:

    lastID= 100000000   # ID's will be 100000000+
    def __init__(self , userName, userMail, userPassword):
        self.userID = self.get_next_ID()
        self.userName = userName
        self.userMail = userMail
        self.userPassword = userPassword
        self.localTimeStamp = datetime.datetime.now()
        self.utcTimeStamp = datetime.datetime.now(datetime.timezone.utc)

    @classmethod
    def get_next_ID(cls):
        cls.lastID +=1
        return cls.lastID





print(localTimeStamp)
print(utcTimeStamp)
print(localTimeStamp_display)
print(utcTimeStamp_display)











