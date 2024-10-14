# GiftMixer project
# R32NOR | ZOLCBYTERS
# 2024

# script containing classes information

import datetime
import tzlocal
import secrets
import string
from collections import OrderedDict  # module to ensure the order of class keys

import database

# connection to database
if __name__ == "__main__":
    db_connection = database.db_switch_on()
    mycursor = db_connection.cursor()

# time variables for time stamping
local_timezone = tzlocal.get_localzone()
local_timestamp = datetime.datetime.now(local_timezone)
utc_timestamp = datetime.datetime.now(datetime.timezone.utc)


class User:
    """
    Represents a user in the GiftMixer project.

    This class stores information about a user, including their ID and the groups they belong to.

    Attributes:
        userID (int): The unique identifier for the user.
        MyGroups (list): A list of groups that the user is a member of
        """

    def __init__(self, userID: int):
        """Initializes a User instance with the given user ID."""

        self.userID = userID
        self.MyGroups = []


class Group:
    """
    Represents a group in the GiftMixer project.

    This class stores information about a group, including its name, admin, members, and event details.

    Attributes:
        groupID (str): The unique identifier for the group (initially empty).
        groupName (str): The name of the group.
        PIN (str): A 6-digit PIN for the group, randomly generated.
        adminID (int): The user ID of the group admin.
        members (list): A list of user IDs representing the members of the group.
        price_limit (str): The price limit for gifts within the group.
        place (str): The location of the group's event.
        meetingDate (str): The date and time of the group's event (in string format).
        deadline (str): The deadline for any necessary group actions (in string format).
        remarks (str): Additional remarks or notes about the group.
        usersFinished (int): The number of users who have completed their tasks for the group.
    """
    def __init__(self, groupName: str, adminID: int):
        """Initializes a Group instance with the group name and admin ID."""
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
    """
    Represents a gift in the GiftMixer project.

    This class holds information about a specific gift, including its name and description.

    Attributes:
        name (str): The name of the gift.
        description (str): A brief description of the gift.
    """

    def __init__(self, name: str, description: str):
        """Initializes a Gift instance with the given name and description."""

        self.name = name
        self.description = description


class GiverData:
    """
    Represents data related to a giver in the GiftMixer project.

    This class holds information about a giver, including their ID, contact details, and associated wishlist information.

    Attributes:
        ID (int): The unique identifier for the giver.
        mail (str, optional): The email address of the giver.
        nick (str, optional): The nickname of the giver.
        receiverName (str, optional): The name of the receiver for whom the giver is buying a gift.
        groupName (str, optional): The name of the group to which the giver belongs.
        wishlist (list, optional): A list of gifts that the giver wants to buy.
    """


    def __init__(self, giverID: int, mail: str = None, nick: str = None, receiverName: str = None, groupName: str = None, wishlist_to_buy: list = None):
        """Initializes a GiverData instance with the given information."""
        self.ID = giverID
        self.mail = mail
        self.nick = nick
        self.receiverName = receiverName
        self.groupName = groupName
        self.wishlist = wishlist_to_buy

    def to_ordered_dict(self):
        """
        Converts the GiverData instance to an ordered dictionary.

        This method returns an OrderedDict where the keys are the attribute names and the values are the attribute values.

        :return: An OrderedDict representation of the GiverData instance.
        :rtype: collections.OrderedDict
        """

        return OrderedDict([
            ("ID", self.ID),
            ("mail", self.mail),
            ("nick", self.nick),
            ("receiverName", self.receiverName),
            ("groupName", self.groupName),
            ("wishlist", self.wishlist)
        ])
