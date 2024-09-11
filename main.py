# #GiftMixer project
# #R32NOR | ZOLCBYTERS
# #2024

# """GiftMixer is a script that helps to split Christmas wishes to people in group.
# One person buys only one present for only one person in the group. The reason for build it was to get one bigger gift than few smaller.
# It prevents too much consumption, saves time on pre-christmas rush and helps to spent money wisely. """

# importing libraries / modules

from datetime import datetime, timezone, timedelta
import os
import re
import json
import zoneinfo
import pytz

import mysql.connector
from mysql.connector import errorcode
import random
import configparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


# import scripts
import login # login, register and account management functions
import classes # classes definitions
import database # database set up
import functions # general purpose functions


print('\nWelcome to Gift Mixer!')
print('A free tool that helps to split Christmas (and not only) wishes to people in group, to reduce consumption, save time and avoid pre-christmas gift-fever and headache :) \n ')

# Log in/ register at first :)
userID = login.main_login()

# db connection
db_connection = login.db_connection
cursor = login.cursor

# run function to set nick for the user (if unknown):
userNick = login.set_user_nick(userID)

# setting User object:
user_object = classes.User(userID)
# PART 1: New group setting: #########################################################################################

# UPDATE: add try-execpt to avoid wrong input error during setting new group
def set_group(userID):
    """FUNCTION: set new instance of Group class, and saving data to
                :param userID
                :return newGroup object
                """


    print('You are creating new group, that your friends can join further.')
    newGroupName = input ('Give a name to your group: ')
    # new Group object
    newGroup = classes.Group(newGroupName, userID)
    newGroup.price_limit = input("What is maximum price of gift? (don't set if you want to): ")
    newGroup.place = input("Where gifts will be exchanged?: ")

    # receive information about timezone
    timezone = functions.timezone_declaration()

    # get information about date and time of meeting
    while True:
        meeting_date_str = str(input("\nWhen group will meet? ('YYYY-MM-DD hh:mm:ss'  24h format): ")).strip()
        meeting_date = functions.get_offset_aware_datetime(meeting_date_str,timezone.zone)
        if meeting_date == None:
            print("Try again.")
            continue
        # eligible value:
        elif meeting_date > datetime.now(tz=timezone):
            break
        else:
            print("You cannot input past date. Input an upcoming date.")
    newGroup.meetingDate = meeting_date

    # get information about date and time of deadline for passing gift list

    while True:
        deadline_str = str(input("\nFinal call date for users to input gift propositions ('YYYY-MM-DD hh:mm:ss'  24h format): ")).strip()
        deadline = functions.get_offset_aware_datetime(deadline_str, timezone.zone)
        if deadline == None:
            print("Try again.")
            continue
        # eligible value:
        elif deadline > datetime.now(tz=timezone):
            break
        else:
            print("You cannot input past date. Input an upcoming date.")
    newGroup.deadline = deadline
    newGroup.remarks = input("Any additional information for the group members: ")

    # Saving Group object attributes
    cursor.execute(
        "INSERT INTO groups_table(groupName, groupPIN, adminID, price_limit, place, meetingDate, deadline, remarks, usersFinished) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (newGroup.groupName, newGroup.PIN, newGroup.adminID, newGroup.price_limit, newGroup.place, newGroup.meetingDate,
         newGroup.deadline, newGroup.remarks, newGroup.usersFinished))

    db_connection.commit()
    cursor.execute("SELECT groupID FROM groups_table WHERE groupName=%s", (newGroupName,))


    # assign new group number to class
    newGroup.groupID = cursor.fetchone()[0]
    # add admin to group members table
    cursor.execute("INSERT INTO group_members (groupID, userID, groupName) VALUES (%s, %s, %s)",
                   (newGroup.groupID, userID, newGroup.groupName))
    db_connection.commit()


# PART 2: joining to group ###########################################################################################

def join_to_group(userID):
    """FUNCTION: function that joins user to group
                :param userID
                :return
                """
    while True:
        groupNumStr = input("Input 9-digit group number that you want to join (or press 'b' to step back): ")
        if groupNumStr.strip().lower() == 'b':
            break
        else:
            group_return = verify_groupNumber(groupNumStr)
            if group_return [0] == True:
                groupNum = group_return[1]
                groupName = group_return[2]
                verify_groupPIN(groupNum, groupName)
                break
# check provided group number:
def verify_groupNumber(groupNumStr):
    """FUNCTION: function that checks if such group exists
                :param group Number (string)
                :return
                """
    # check if length of group number is correct
    if len(groupNumStr) !=9:
        print("Invalid group number length")
        return None
    try:
        groupNum = int(groupNumStr)
    except ValueError:
        print("Invalid group number format.")
        return None
    # retrieving group name from db
    cursor.execute("SELECT groupName FROM groups_table WHERE groupID = %s", (groupNum,))
    db_fetch = cursor.fetchone()
    if db_fetch:
        groupName = db_fetch[0]
        return True, groupNum, groupName
    else:
        print("Such group does not exist.")
        return None

# veryfing PIN and add user to database if correct
def verify_groupPIN(groupID, groupName):
    """FUNCTION: function that verifies if PIN is correct
                :param group number
                :return
                """
    userPIN = input("Type in PIN to access the group: ")
    if len(userPIN) == 6:
        cursor.execute("SELECT groupPIN FROM groups_table WHERE groupID=%s", (groupID,))
        dbPIN = cursor.fetchone()[0]
        if userPIN == dbPIN:
            cursor.execute("INSERT INTO group_members (groupID, userID, groupName) VALUES (%s, %s, %s)", (groupID, userID, groupName))
            db_connection.commit()
            print(f"You are succesfully added to group {groupID}, {groupName}! Please choose MyGroups to add your wishes :)")
    else:
        print("PIN incorrect. Try again.")

# PART 3: My Groups operations: ######################################################################################
def my_groups(userID):
    """FUNCTION: function that enters the group management menu
                :param userID
                :return
                """
    # searching groups where user is an admin:
    cursor.execute("SELECT groupID, groupName FROM groups_table WHERE adminID=%s", (userID,))
    adminGroups = cursor.fetchall()
    # searching other groups where user is a member:
    cursor.execute(
        "SELECT groupID, groupName FROM group_members WHERE userID=%s AND groupID NOT IN (SELECT groupID FROM groups_table WHERE adminID=%s) ",
        (userID, userID))
    otherGroups = cursor.fetchall()

    allGroups = [i[0] for i in adminGroups]+[j[0] for j in otherGroups]
    print("\nYour Groups:")

    # displaying both admin groups and joined:
    if len(adminGroups) != 0 and len(otherGroups) != 0:
        print("Groups under your management:")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for i in adminGroups:
            print(f"{i[0]:<20}{i[1]:<20}")
        print("\nOther groups where you belong as a guest:")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for i in otherGroups:
            print(f"{i[0]:<20}{i[1]:<20}")
    # displaying only admin groups:
    elif len(adminGroups) != 0 and len(otherGroups) == 0:
        print("\nGroups under your management:")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for i in adminGroups:
            print(f"{i[0]:<20}{i[1]:<20}")
    # displaying only joined groups:
    elif len(adminGroups) == 0 and len(otherGroups) != 0 :
        print("\nGroups that you have joined:\n")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for i in otherGroups:
            print(f"{i[0]:<20}{i[1]:<20}")
    # no groups joined:
    else:
        print("You are not a member of any group yet. \nSet up new group or join to one if you received an invitation.")
        return
    # Choosing the group number that user want to operate in:
    while True:
        try:
            chosenGroup = int(input("\nChoose the group number to see group details:\n"))
            break
        except ValueError:
            print("Incorrect value.")
    # Entering group that user wants to operate in:
    enter_the_group(userID, allGroups, chosenGroup)

# Enter the group function:
def enter_the_group(userID, allGroups, chosenGroup):
    """FUNCTION: function for create instance of the class and assign values from db to class attribute
                :param userID, allGroups (list of groups that user is a member) this function has to be, chosen group ID
                :return
                """

    if chosenGroup in allGroups:
        print(f"\nGroup {chosenGroup} information:")
        # querying for obtain group information data:
        cursor.execute("SELECT * FROM groups_table WHERE groupID=%s", (chosenGroup,))
        groupData = cursor.fetchall()[0]    # saving collected data as a tuple

        # querying for group members list:
        cursor.execute(
            "SELECT group_members.userID, users.userNick FROM group_members \
            JOIN users ON group_members.userID = users.userID \
            WHERE groupID = %s \
            ORDER BY group_members.userID;", (chosenGroup,))
        db_fetch = cursor.fetchall()
        groupMembers = [i[0] for i in db_fetch]
        groupMembersWithNicks = [i for i in db_fetch]

        # assign values to class:
        group_object = classes.Group(groupData[1], groupData[3])
        group_object.groupID = groupData[0]
        group_object.PIN = groupData[2]
        group_object.members = groupMembers
        group_object.price_limit = groupData[4]
        group_object.place = groupData[5]
        group_object.meetingDate = groupData[6]
        group_object.deadline = groupData[7]
        group_object.remarks = groupData[8]

        # fetching group admin nick from db
        cursor.execute(
            "SELECT userID, userNick FROM users WHERE userID = (SELECT adminID FROM groups_table WHERE groupID = %s)",
            (chosenGroup,))
        adminData = cursor.fetchall()[0]

        # function for displaying group information:
        def group_info_display():
            """FUNCTION: function for displaying chosen group data
                        :param
                        :return
                        """
            print(f"Admin of this group is: {adminData[1]} (#{adminData[0]}), other members are:")
            # displaying member of selected group
            n = 1
            for i in groupMembersWithNicks:
                if i[0] != adminData[0]:
                    print(f"{n:>3}. {i[1]:<10}(#{i[0]})")
                    n+=1
                else:
                    pass
            print(f"\nPrice limit for gift is: {group_object.price_limit}\nPlace of meeting: {group_object.place},\nDate of meeting: {group_object.meetingDate},\nLast call for pushing wishlist: {group_object.deadline}")
            print(f"Additional info from group manager: \n{group_object.remarks}\n")

        group_info_display() # call the function

        # now checks if user has already added list of gifts:
        giftsIn = gifts_added_check(userID, group_object.groupID)

        if giftsIn[0] == True:  # If list of gift is stated in the group- than user can see or edit it.
            group_operations(group_object, userID)

        else: # If list of gifts has not been stated- than user has to declaire it:
            prompt3 = "Do you want to add gift list now? (y/n): "
            addNow = input(prompt3)
            if addNow.strip().lower() == 'y':
                add_gifts(userID, group_object.groupID )
            elif addNow.strip().lower() == "n":
                return None
            else:
                print("Wrong input- try again.")
    else:
        print("You are not a member of chosen group.")

# Checks if user has added the wishlist:
def gifts_added_check(userID, groupID):
    """FUNCTION: function that checks if user passed gift list do the group
                :param userID, groupID
                :return T/F
                """
    cursor.execute("SELECT gift_1, gift_2, gift_3 FROM group_members WHERE groupID = %s AND userID = %s", (groupID, userID))
    db_fetch = cursor.fetchone()
    giftList = [i for i in db_fetch]
    # loop for check how many wishes was added do db:
    gi= 0
    for gift in giftList:
        #number of gifts saved in db
        if gift == None:
            pass
        else:
            gi+=1
    if gi == 0:
        print("Any wish was added to group.")
        return (False,)
    else:
        print(f"\nYou've got {gi} gift saved in group." if gi == 1 else f"You've got {gi} gifts saved in group.")
        return (True, giftList)

# function for add new gifts if group is empty for current user
def add_gifts(userID, groupID, editmode=False):
    """FUNCTION: function to add gifts when user hasn't done it before
                :param user ID, group ID
                :return T/F
                """
    # ensure editmode is a boolean
    if not isinstance(editmode, bool):
        raise ValueError("The parameter 'editmode' must be a boolean value.")

    # assing correct prompt value (according if it is a first assignement of gifts or editing of gift list)
    prompt = "Now think about your 3 wishes :)" if editmode == False else "Save again your wishes. One at least - three maximum."
    print(prompt)
    gifts = []  #list to contain gift objects
    gifts_jsons = [] # list for containing
    db_gifts_columns = ['gift_1', 'gift_2', 'gift_3'] # list with column names where gifts are containded
    n = 0
    # loop to avoid asking in first input:
    for n in range (0,3):
        if n > 0:  # condition to skip first turn
            proceed = more_gifts_question()
            if proceed == True:
                pass
            else:
                break
        else: # for n=0
            pass

        giftName = input("Name of dream gift: ")
        giftDescription = input("Description of your wish: ")
        gift = classes.Gift(giftName, giftDescription) # object setting
        gifts.append(gift) # contain object in list
        gift_json = json.dumps(gift.__dict__) # serialize object attributes in JSON notation
        gifts_jsons.append(gift_json) # contain json in list

    # preparing sql query to pass wishlist to db
    set_clauses = ", ".join([f"{db_gifts_columns[i]} = %s" for i in range(len(gifts_jsons))])
    sql_query = f"UPDATE group_members SET {set_clauses} WHERE groupID = %s AND userID = %s;"
    params = gifts_jsons + [groupID, userID]
    cursor.execute(sql_query, params)

    # check for number of gifts (

    # update number of gifts in group_members table in db
    query = "UPDATE group_members SET number_of_gifts = %s WHERE groupID = %s AND userID = %s;"
    cursor.execute(query, (len(gifts), groupID, userID))

    # increase the number of users that pushes gift list to group:
    if not editmode:
        # increase the number of users that pushes gift list to group:
        cursor.execute("UPDATE groups_table SET usersFinished = usersFinished + 1  WHERE groupID = %s;", (groupID,))

    db_connection.commit()

# function to ask user to continue gifts adding
def more_gifts_question():
    """FUNCTION: function to ask user for adding more gifts
                :param none
                :return T/F
                """

    proceedPrompt = "Do you want to add next gift proposition? (y/n): "
    while True:
        proceedAsk = input(proceedPrompt)
        if proceedAsk.strip().lower() == 'y':
            return True
        elif proceedAsk.strip().lower() == "n":
            return False
        else:
            print("Wrong input- try again.")

# GROUP OPERATIONS (if wish list already stated)
def group_operations(group_object, userID, adminMode=False):
    """FUNCTION: function for operate on gifts that are stated in group
                :param group ID, user ID, gift list (list of jsons fetched from db)
                :return
                """

    adminMode = True if userID == group_object.adminID else False
    # ensure editmode is a boolean
    if not isinstance(adminMode, bool):
        raise ValueError("The parameter 'adminMode' must be a boolean value.")

    while True:
        print("\nOPTIONS:")
        # Displaying varies prompt in case user is admin or not.
        if adminMode == True:
            print("[1] Preview gift list \n[2] Edit gift list \n[3] Run Gift Mixer! \n[4] Remind group PIN \n[e] Exit to Main Menu")
        else:
            print("[1] Preview gift list \n[2] Edit gift list \n[e] Exit to Main Menu")
        program_mode = input('\nChoose mode : ')

        if program_mode.strip() == '1':    # see gift list
            print("\nYour wishes:")
            # fetching current gift list from db
            cursor.execute("SELECT gift_1, gift_2, gift_3 FROM group_members WHERE groupID = %s AND userID = %s",
                           (group_object.groupID, userID))
            db_fetch = cursor.fetchone()
            giftListJSON = [i for i in db_fetch]
            n = 1
            #iterate trough json-gift list:
            for wish in giftListJSON:
                if wish != None:
                    gift_dict = json.loads(wish) # retrieve dicts from json
                    gift_instance = classes.Gift(gift_dict.get('name'), gift_dict.get('description')) # set instance of Gift class
                    print(f"{n}. Gift name: {gift_instance.name:<20}Gift description: {gift_instance.description}") # displaying gift list with formatting
                else:
                    pass
                n+=1

        elif program_mode.strip() == '2':    # edit gift list
            # get current local timestamp
            currentLocalTime_offsetAware = functions.py_local_timestamp()

            # deadline in current group
            deadline = group_object.deadline
            print("is dt aware? ", functions.is_aware(deadline))

            # check if datetime is naive or aware:
            if functions.is_aware(deadline) == True:
                pass
            else:
                deadline = functions.get_offset_aware_datetime(str(deadline),None)

            print(currentLocalTime_offsetAware)
            print(deadline)

            if currentLocalTime_offsetAware > deadline:
                print("TOO LATE TOO LATE!")
            else:
                print("NOT TOO LATE")











            #
            # print("deadline: ", local_timezone, type(group_object.deadline), group_object.deadline)
            #
            # deadline_from_db = group_object.deadline
            # timezone_str = deadline_from_db.tzname()
            #
            # deadline_to_compare = functions.get_offset_aware_datetime(str(group_object.deadline),timezone_str)
            #
            #
            #
            # print(currentLocalTime_offsetAware)
            # print(deadline_to_compare)
            # print(timezone_str)
            #
            # if currentLocalTime_offsetAware > deadline_to_compare:
            #     print("TOO LATE TOO LATE!")
            # else:
            #     print("NOT TOO LATE")

            # check if current date is before deadline
            # deadline_fetched = functions.datetime_for_compare(group_object.groupID, userID)
            # if deadline_fetched != None:
            #     print(deadline_fetched)
            #     print(type(deadline_fetched))




            print("PAMIĘTAJ O DODANIU WARUNKU Z DATĄ (PRZEKROCZENIE DEADLINE)")

            # Wishlist edit type question:
            print("Now you will edit your wishes.")
            while True:
                typeOfEdit = input("\nPress [a] for change all gifts or [s] for change gifts one by one: ")
                # user wants to overwrite gift list- we run add_gifts function but in edit mode
                if typeOfEdit.strip().lower() == 'a':
                    add_gifts(userID, group_object.groupID, editmode = True)
                    break

                # edit list one by one:
                elif typeOfEdit.strip().lower() == 's':
                    print("\nYou'll be changing gift in the wish list one by one.")

                    db_gifts_columns = ['gift_1', 'gift_2', 'gift_3']  # list with column where gifts are contained
                    # fetching current gift list from db
                    clause = ", ".join([f"{db_gifts_columns[i]}" for i in range(len(db_gifts_columns))])
                    cursor.execute(f"SELECT {clause} FROM group_members WHERE groupID = %s AND userID = %s", (group_object.groupID, userID))
                    db_fetch = cursor.fetchone()
                    giftListJSON = [i for i in db_fetch]  # list with gifts in json format fetched from db
                    gifts = []  # list to contain gift objects
                    gifts_jsons = []  # list for containing JSONs

                    n=0
                    for n in range(len(giftListJSON)):
                        if giftListJSON[n] != None:
                            gift_dict = json.loads(giftListJSON[n])  # retrieve dict from JSON
                            gift_instance = classes.Gift(gift_dict.get('name'), gift_dict.get('description'))  # set instance of Gift class
                            # displaying gift list n-position with formatting
                            print(f"Gift no. {n + 1}. name: {gift_instance.name:<20}Gift description: {gift_instance.description}")

                            # asking if user wants to change this gift:
                            prompt = "Do you want to replace this gift? Press [y] if yes, [d] for delete this wish. Press ENTER if you want to leave this gift in wishlist: "
                            while True:
                                goFurther = input(prompt)
                                if goFurther == "":
                                    gifts.append(gift_instance)
                                    break
                                elif goFurther == 'd':
                                    # gifts.append(None)
                                    break
                                elif goFurther.strip().lower() == 'y':
                                    giftName = input("Name of dream gift: ")
                                    giftDescription = input("Description of your wish: ")
                                    gift_changed = classes.Gift(giftName, giftDescription)  # object setting
                                    gifts.append(gift_changed)  # adding new gift object to list
                                    print(f"You have edited gift no. {n + 1}. name: {gift_changed.name:<20}Gift description: {gift_changed.description}") # displaying added gift
                                    break
                                else:
                                    print("Incorrect input.")
                                    continue
                        # now case when current position of gift list is NULL
                        else:
                            prompt2 = f"\nGift no. {n + 1}. is empty. Do you want to set new wish? (y/n): "
                            goFurther2 = input(prompt2)

                            if goFurther2.strip().lower() == 'y':
                                giftName = input("Name of dream gift: ")
                                giftDescription = input("Description of your wish: ")
                                gift_changed = classes.Gift(giftName, giftDescription)  # object setting
                                gifts.append(gift_changed)  # adding new gift object to list
                                print(f"Gift no. {n + 1}. name: {gift_changed.name:<20}Gift description: {gift_changed.description}")

                            elif goFurther2.strip().lower() == 'n':
                                pass
                            else:
                                print("Incorrect input.")

                    # check if there is no empty list. If yes- then starts add_gifts() function to add at least one gift.
                    if len(gifts) == 0:
                        print("Your gift list is empty. Please set up at least one gift :) ")
                        add_gifts(userID, group_object.groupID, editmode=True)
                        break

                    nonNoneGifts = len(gifts) # number of none gift to pass to db

                    # loop for adding empty positions to list
                    while len(gifts) < len(db_gifts_columns):
                        gifts.append(None)

                    # loop for serialize objects as JSONs:
                    n = 0
                    for n in range(0, 3):
                        if gifts[n] != None:
                            gift_json = json.dumps(gifts[n].__dict__)  # serialize object attributes in JSON notation
                            gifts_jsons.append(gift_json)  # contain JSON in list
                        else:
                            gifts_jsons.append(None) # if object is None then insert empty position

                    # preparing sql query
                    set_clause = ", ".join([f"{db_gifts_columns[i]} = %s" for i in range(len(gifts_jsons))])
                    sql_query = f"UPDATE group_members SET {set_clause} WHERE groupID = %s AND userID = %s;"
                    params = gifts_jsons + [group_object.groupID, userID]
                    cursor.execute(sql_query, params)

                    # update number of gifts in db
                    cursor.execute("UPDATE group_members SET number_of_gifts = %s WHERE groupID = %s AND userID = %s",
                                   (nonNoneGifts, group_object.groupID, userID))
                    db_connection.commit()
                    break
                else:
                    print('Input incorrect.\nTry again.\n')

        elif program_mode.strip() == '3' and group_object.adminID == userID: # option only for admins
            run_mixer(group_object)

        elif program_mode.strip() == '4' and group_object.adminID == userID: # option only for admins:
            print(f"{group_object.groupName} group PIN is: {group_object.PIN}")

        elif program_mode.strip().lower() == 'e':  # exit
            return

        else:
            print("Wrong input. Choose correct option.\n")

def run_mixer(group_object):

    # prep.1: fetching usersID from selected group who passed wishlist
    query = "SELECT userID FROM group_members WHERE groupID = %s AND number_of_gifts > 0 ORDER BY userID;"
    cursor.execute(query, (group_object.groupID,))
    dbfetch = cursor.fetchall()
    # giceivers = [i[0] for i in dbfetch] #retrieving users id from db fetch
    giver_list= [i[0] for i in dbfetch] #retrieving users id from db fetch
    receiver_list = giver_list.copy() # receiver_list = []  # list for contain userID to whom gift will be bought
    giceiver_pairs = []  # list for contain dicts {giver:receiver}
    giver_data_list = []  # list for contain giver data objects (ID, mail, nick, wishlist to buy)

    # prep. 2: pulling wishlists
    # query for fetching gift list from db
    query = f"SELECT userID, gift_1, gift_2, gift_3 FROM group_members WHERE groupID = %s AND number_of_gifts > 0 ORDER BY userID;"
    cursor.execute(query, (group_object.groupID,))
    db_fetch = cursor.fetchall()
    wishlists = {} # dict for contain each user wishlist
    # loop for retrieving wishlists
    for row in db_fetch:
        key = row[0]
        values = []
        # fetch gift items from db table, drop nulls and unjsonize existing ones
        n = 1
        for n in range(1,4):
            if row[n] != None:
                unjsonized_value = json.loads(row[n])
                values.append(unjsonized_value)
        # creating dict {userID: wishlist}
        userWishes = {key:values}
        wishlists.update(userWishes) # adding position to dictionary

    # prep. 3: fetching emails and nicknames from db for mailing
    query_list = ", ".join(str(ids) for ids in giver_list)
    query = f"SELECT userID, userNick, userMail  FROM users WHERE userID IN ({query_list}) ORDER BY userID;"
    cursor.execute(query)
    db_fetch = cursor.fetchall()
    mail_addresses = {} # dict for contain IDs, nicknames and mails
    for pos in db_fetch:
        pair = {pos[0]:(pos[1], pos[2])} # creating pair with ID and tuple (nickname and email of giver)
        mail_addresses.update(pair) # adding pair do dict

# START MIXER- creating pairs giver-receiver and giver-wishlist to buy

    # shuffle receiver list first, then pair giver with receiver
    random.shuffle(giver_list)
    #iterate trough givers and receivers lists to
    for giver in giver_list:
        if giver == receiver_list[0]:
            receiver_list.append(receiver_list.pop(0))
        receiver = receiver_list.pop(0)
        passPair = {giver : receiver}  # joining IDs into dictionary
        giverNick = mail_addresses.get(giver)[0]
        giverMail = mail_addresses.get(giver)[1]
        receiverName = mail_addresses.get(receiver)[0]
        # setting instance of Giver_data class
        giver_data_object = classes.Giver_data(
            giver, giverMail, giverNick, receiverName, group_object.groupName, wishlists.get(receiver))
        # append elements to lists:
        giceiver_pairs.append(passPair)
        giver_data_list.append(giver_data_object)

    # Pushing obtained lists to db:
    # 1. Passing giver-receiver list to groups_table:
    giceiver_pairs_json = json.dumps(giceiver_pairs) # serialize object attributes in JSON notation
    query = f"UPDATE groups_table SET giver_receiver_pairs = %s WHERE groupID = %s"
    cursor.execute(query,(giceiver_pairs_json, group_object.groupID))
    db_connection.commit()

    # 2. Passing giver_data_object to db:
    # iterate trough user-objects to serialize each one as a json and push to db
    for gvr in giver_data_list:
        # set order of keys in class:
        gvr_ordered = gvr.to_ordered_dict()
        gvr_json = json.dumps(gvr_ordered)
        # preparing mysql statement:
        query = f"UPDATE group_members SET giver_object = %s WHERE groupID = %s AND userID = %s"
        params = (gvr_json, group_object.groupID, gvr.ID)
        cursor.execute(query, params)
        db_connection.commit()

    # MAILING (Send emails to givers)
    def mailing_from_main():
        # iterate trough user-objects to send personalized mail to each one
        for giver in giver_data_list:
            # subject setting
            subject = f"{giver.nick} your GiftMixer group is ready! Prepare to be a real Giver and choose gift for the other one! :) "

            # email body setting
            wshlst = giver.wishlist  # taking wishlist from object
            wishDisplay = "\n"  # string to be put into mail
            # iterating trough wishes to add to string
            try:
                for wish in wshlst:
                    wishName = wish.get("name")
                    wishDesc = wish.get("description")
                    wishIndex = str(wshlst.index(wish) + 1)
                    wishDisplay = f"{wishDisplay}{wishIndex}. Gift name: {wishName}     Description: {wishDesc} \n"
            except Exception as e:
                print(f"Error occur: {e}")

            # addition to body text with remark from group manager (if he/she passed it)
            bodyAddition = ""
            if group_object.remarks != "":
                bodyAddition += "Additional information for the group members: " + group_object.remarks

            # fetching group admin nick from db
            cursor.execute("SELECT userID, userNick FROM users WHERE userID = %s", (group_object.adminID,))
            adminData = cursor.fetchall()[0]
            groupManagerID = adminData[0]
            groupManagerNick = adminData[1]

            # full body
            body = f"""Hi {giver.nick},\n\n{group_object.groupName} group has been completed and GiftMixer shuffled wishlists for you and your friends. Now you can fulfill {giver.receiverName} dream by buying one of the gifts from below whishlist:
    
{wishDisplay}
Remember to not wait on the last call for buying gift- do it in advance! :) Price limit in {group_object.groupName} group is {group_object.price_limit}.

Your group meets on {group_object.meetingDate}.
Place of meeting is {group_object.place}.
{bodyAddition}
{group_object.groupName} group manager is {groupManagerNick} ({groupManagerID}).

Don't forget to signt the gift with receiver nick name!

Thanks for using GiftMixer and have a lot fun with gift exchange! ;)
With \u2661 GiftMixer Team."""

            # run mailing function
            functions.send_email(giver.mail, subject, body)
    # run function
    mailing_from_main()



# PART 4: Profile settings
def profile_settings():

    while True:
        print('\n[1] Change nick \n[2] Change password \n[b] Back to main menu')
        section_mode = input('Choose mode : ')

        if section_mode.strip().lower() == 'b':
            break

        elif section_mode.strip() == '1':   # nick edit
            global userNick
            newUserNick = login.change_nick(userID, userNick)
            # condition to step back if user nich hasn't been changed
            if newUserNick == None:
                continue
            else:
                userNick = newUserNick  # overwiting userNick variable
            return userNick

        elif section_mode.strip() =='2':    # password edit
            login.update_password(userID, userNick)

        else:
            print("Wrong input. Try again.\n")

def main_menu():

    while True:
        print('\n[1] Set new group \n[2] Join to group \n[3] My groups \n[4] Profile settings \n[x] Close program')
        program_mode = input('Choose mode : ')
        if program_mode.strip() == '1':    # starting new group
            set_group(userID)
        elif program_mode.strip() == '2':    # join to group
            join_to_group(userID)
        elif program_mode.strip() == '3':    # user group operations
            mygroups = my_groups(userID)
        elif program_mode.strip() == '4':  # profile settings
            profile_settings()
        elif program_mode.strip().lower() == 'x':  # close program
            login.terminate_process()
        else:
            print("Wrong input. Try again.\n")

if __name__ == "__main__":
    main_menu()


















