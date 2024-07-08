# #GiftMixer project
# #R32NOR | anklebiters.
# #2024

# """GiftMixer is a script that helps to split Christmas wishes to people in group.
# One person buys only one present for only one person in the group. The reason for build it was to get one bigger gift than few smaller.
# It prevents too much consumption, saves time on pre-christmas rush and helps to spent money wisely. """

# importing libraries / general modules

import re
import json
import mysql.connector
from mysql.connector import errorcode as err

import classes
import database


# importing scripts
import login # script with login, register and account management functions:

print('\nWelcome to Gift Mixer!')
print('A free tool that helps to split Christmas (and not only) wishes to people in group, to reduce consumption, save time and avoid pre-christmas gift-fever and headache :) \n ')

# Log in/ register at first :)
userID = login.main()

# db connection
db_connection = login.db_connection
cursor = login.cursor

# Setting nick for the user (if unknown):
cursor.execute(f"SELECT userNick FROM users WHERE userID='{userID}'")
userNick = cursor.fetchone()[0]
while not  userNick:
    new_Nick = input(f"\nPlease set up an unique nick for your account: ")
    try:
        cursor.execute(f"UPDATE users SET userNick = '@paramName' WHERE userID={userID}")
        db_connection.commit()
        print(f'Hi {new_Nick}',)
        break
    except mysql.connector.IntegrityError as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            print('Chosen nick has been already occupied. Please choose another one.')
else:
    print(f'Hi {userNick},')

# setting User object:
UserObj = classes.User(userID)

# OPTION 1: New group setting: #########################################################################

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
    newGroup.meetingDate = input("When group will meet? (YYYY-MM-DD hh:mm:ss  24h format): ")
    newGroup.deadline = input("Final call date for users to input gift propositions (YYYY-MM-DD hh:mm:ss  24h format): ")
    newGroup.remarks = input("Any additional information for the group members: ")


    # Saving Group object attributes
    cursor.execute(f"INSERT INTO groups_table(groupName, groupPIN, adminID, price_limit, place, meetingDate, deadline, remarks, usersFinished) \
                    VALUES ('{newGroup.groupName}', '{newGroup.PIN}', '{newGroup.adminID}',\
                    '{newGroup.price_limit}', '{newGroup.place}', '{newGroup.meetingDate}', '{newGroup.deadline}', '{newGroup.remarks}', '{newGroup.usersFinished}')")
    db_connection.commit()
    cursor.execute(f"SELECT groupID FROM groups_table WHERE groupName='{newGroupName}'")

    # assign new group number to class
    newGroup.groupID = cursor.fetchone()[0]
    # add admin to group members table
    cursor.execute(
        f"INSERT INTO group_members (groupID, userID, groupName) VALUES ('{newGroup.groupID}', '{userID}', '{newGroup.groupName}')")
    db_connection.commit()


# OPTION 2: joining to group #########################################################################

def join_to_group(userID):
    """FUNCTION: function that joins user to group
                :param userID
                :return
                """
    while True:
        groupNumStr = input("Input 9-digit group number that you want to join (or press 'B' to step back): ")
        if groupNumStr.strip().upper() == 'B':
            break
        else:
            group_return = verify_groupNumber(groupNumStr)
            if group_return [0] == True:
                groupNum = group_return[1]
                groupName = group_return[2]
                verify_PIN(groupNum, groupName)
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
def verify_PIN(groupID, groupName):
    """FUNCTION: function that verifies if PIN is correct
                :param group number
                :return
                """
    userPIN = input("Type in PIN to access the group: ")
    if len(userPIN) == 6:
        cursor.execute("SELECT groupPIN FROM groups_table WHERE groupID=%s", (groupID,))
        dbPIN = cursor.fetchone()[0]
        if userPIN == dbPIN:
            cursor.execute(f"INSERT INTO group_members (groupID, userID, groupName) VALUES ('{groupID}', '{userID}', '{groupName}')")
            db_connection.commit()
            print(f"You are succesfully added to group {groupID}, {groupName}! Please choose MyGroups to add your wishes :)")
    else:
        print("PIN incorrect. Try again.")


# OPTION 3: My Groups operations: #########################################################################
def my_groups(userID):
    """FUNCTION: function that enters the group management menu
                :param userID
                :return
                """
    # searching groups where user is an admin:
    cursor.execute(f"SELECT groupID, groupName FROM groups_table WHERE adminID={userID}")
    adminGroups = cursor.fetchall()
    # searching other groups where user is a member:
    cursor.execute(f"SELECT groupID, groupName \
    FROM group_members \
    WHERE userID={userID} AND groupID NOT IN (\
    SELECT groupID FROM groups_table WHERE adminID={userID}) ")
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
        cursor.execute(f"SELECT * FROM groups_table WHERE groupID={chosenGroup}")
        groupData = cursor.fetchall()[0]    # saving collected data as a tuple

        # querying for group members list:
        cursor.execute(f"\
                        SELECT group_members.userID, users.userNick\
                        FROM group_members \
                        JOIN users\
                        ON group_members.userID = users.userID\
                        WHERE groupID = {chosenGroup}\
                        ORDER BY group_members.userID;")
        db_fetch = cursor.fetchall()
        groupMembers = [i[0] for i in db_fetch]
        groupMembersWithNicks = [i for i in db_fetch]

        # assign values to class:
        group_object = classes.Group(groupData[1], groupData[3])
        group_object.groupID = groupData[0]
        group_object.PIN = groupData[2]
        group_object.members = groupMembers
        group_object.price_limit = groupData[4]
        group_object.deadline = groupData[5]
        group_object.place = groupData[6]
        group_object.meetingDate = groupData[7]
        group_object.remarks = groupData[8]

        # fetching group admin nick from db
        cursor.execute(f"SELECT userID, userNick FROM users WHERE userID = (SELECT adminID FROM groups_table WHERE groupID = {chosenGroup})")
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
            print(f"\nPlace of meeting:{group_object.place},\nDate of meeting: {group_object.meetingDate} \nPrice limit for gift is: {group_object.price_limit}.")
            print(f"Additional info from group manager: \n{group_object.remarks}\n")

        group_info_display() # call the function

        # now checks if user has already added list of gifts:
        giftsIn = gifts_added_check(userID, group_object.groupID)

        if giftsIn[0] == True:  # If list of gift is stated in the group- than user can see or edit it.
            group_operations_for_users(group_object.groupID, userID)

        else: # If list of gifts has not been stated- than user has to declaire it:
            print("ADD A QUESTION- DO YOU WANT TO ADD GIFT LIST?")
            add_gifts(userID, group_object.groupID )
    else:
        print("You are not a member of chosen group.")

# Checks if user has added the wishlist:
def gifts_added_check(userID, groupID):
    """FUNCTION: function that checks if user passed gift list do the group
                :param userID, groupID
                :return T/F
                """
    cursor.execute(f"SELECT gift_1, gift_2, gift_3 FROM group_members WHERE groupID = {groupID} AND userID = {userID}")
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
                # if user don't want to push another wishes- then below loop fills the lists with empty positions
                # this is for using that function again when user want to edit all gifts
                gift = None
                for position in range (n,3):
                    gifts.append(gift)  # contain object in list
                    gifts_jsons.append(gift)  # contain json in list
                break
        else: # for n=0
            pass

        giftName = input("Name of dream gift: ")
        giftDescription = input("Description of your wish: ")
        gift = classes.Gift(giftName, giftDescription) # object setting
        gifts.append(gift) # contain object in list
        gift_json = json.dumps(gift.__dict__) # serialize object attributes in JSON notation
        gifts_jsons.append(gift_json) # contain json in list

    # preparing sql query
    set_clauses = ", ".join([f"{db_gifts_columns[i]} = %s" for i in range(len(gifts_jsons))])
    sql_query = f"UPDATE group_members SET {set_clauses} WHERE groupID = %s AND userID = %s;"
    params = gifts_jsons + [groupID, userID]

    cursor.execute(sql_query, params)

    # increase the number of users that pushes gift list to group:
    if not editmode:
        cursor.execute("UPDATE groups_table SET usersFinished = usersFinished + 1  WHERE groupID = %s", (groupID,))
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
def group_operations_for_users(groupID, userID):
    """FUNCTION: function for operate on gifts that are stated in group
                :param group ID, user ID, gift list (list of jsons fetched from db)
                :return
                """

    while True:
        print("\nOPTIONS:")
        print("[1] Preview gift list \n[2] Edit gift list \n[3] Exit group")
        program_mode = input('\nChoose mode : ')

        if program_mode.strip() == '1':    # see gift list
            print("\nYour wishes:")
            # fetching current gift list from db
            cursor.execute(f"SELECT gift_1, gift_2, gift_3 FROM group_members WHERE groupID = {groupID} AND userID = {userID}")
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

            print("PAMIĘTAJ O DODANIU WARUNKU Z DATĄ (PRZEKROCZENIE DEADLINE)")

            print("Now you will edit your wishes.")
            typeOfEdit = input("\nPress [A] for change all gifts or [S] for change gifts one by one: ")
            while True:
                # user wants to overwrite gift list- we run add_gifts function but in edit mode
                if typeOfEdit.strip().upper() == 'A':
                    add_gifts(userID, groupID, editmode = True)
                    break

                # editing list one by one
                elif typeOfEdit.strip().upper() == 'S':
                    print("\nYou'll be changing gift in the wish list one by one.")

                    db_gifts_columns = ['gift_1', 'gift_2', 'gift_3']  # list with column where gifts are contained
                    # fetching current gift list from db
                    clause = ", ".join([f"{db_gifts_columns[i]}" for i in range(len(db_gifts_columns))])
                    cursor.execute(f"SELECT {clause} FROM group_members WHERE groupID = %s AND userID = %s", (groupID, userID))
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
                            prompt = "Do you want to replace this gift? Press 'y' if yes, 'd' for erase this wish. Press ENTER if you want to leave this gift: "
                            goFurther = input(prompt)
                            while True:
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
                        # now case when current position of gift list is NULL
                        else:
                            prompt2 = f"\nGift no. {n + 1}. is empty. Do you want to set new wish? (y/n)"
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

                    # check if there is no empty list
                    if len(gifts) == 0:
                        print("Your gift list is empty. Please set up at least one gift :) ")
                        add_gifts(userID, groupID, editmode=True)
                        break

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
                    set_clauses = ", ".join([f"{db_gifts_columns[i]} = %s" for i in range(len(gifts_jsons))])
                    sql_query = f"UPDATE group_members SET {set_clauses} WHERE groupID = %s AND userID = %s;"
                    params = gifts_jsons + [groupID, userID]
                    cursor.execute(sql_query, params)
                    db_connection.commit()
                    break
                else:
                    print('Input incorrect.\nTry again.\n')


        elif program_mode.strip() == '3':  # exit
            return
            # elif program_mode.strip() == '3':  # Settings
        else:
            print("Wrong input- choose option 1, 2 or 3.\n")


def main_menu():

    while True:
        print('\n[1] Set new group \n[2] Join to Group \n[3] MyGroups \n[4] My Account')
        program_mode = input('Choose mode : ')
        if program_mode.strip() == '1':    # starting new group
            set_group(userID)
        elif program_mode.strip() == '2':    # join to group
            join_to_group(userID)
        elif program_mode.strip() == '3':    # showing user groups
            mygroups = my_groups(userID)
        # elif program_mode.strip() == '3':  # Settings
        else:
            print("Wrong input- choose option 1, 2, 3 or 4.\n")

if __name__ == "__main__":
    main_menu()






# TO DO:
# [1]!!!: Rewrite sql queries using parameterized queries
















