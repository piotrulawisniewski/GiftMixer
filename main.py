# GiftMixer project
# R32NOR | ZOLCBYTERS
# 2024

"""GiftMixer is a script that helps to split Christmas wishes to people in group.
One person buys only one present for only one person in the group. The reason for build it was to get one bigger gift
than few smaller.
It also prevents too much consumption, saves time on pre-christmas rush and helps to spent money wisely. """

# importing libraries / modules

from datetime import datetime, timezone
import json
import pytz
from typing import Literal, Optional
import mysql.connector
from mysql.connector import IntegrityError
import random

import database
# import project scripts
import login  # login, register and account management functions
import classes  # classes definitions
import functions  # general purpose functions
from logger_config import logger, logger_withDisplay
import wishAI_Gemini_API

print('\nWelcome to Gift Mixer!')
print('A free tool that helps to split Christmas (and not only) wishes to people in group, \
to reduce consumption, save time and avoid pre-christmas gift-fever and headache :) \n ')

# Log in/ register at first :)
userID = login.main_login()

# db connection parameters
db_connection = login.db_connection
cursor = login.cursor

# run function to set nick for the user (if unknown):
user_nick = login.set_user_nick(userID)

# setting User object:
user_object = classes.User(userID)


# PART 1: New group setting: ###########################################################################################
# Create a new group, set its details, and save it to the database
def set_group(userID: int):
    """
    Creates a new group with relevant information such as meeting date,
    deadline, price limit, and location, and stores it in the database.
    The group admin (the user who creates the group) is also added to the
    group members table. Handles database errors and ensures valid date
    and time input for the meeting and deadline.

    :param userID: The ID of the user creating the group (admin).

    :raises mysql.connector.Error: If a database error occurs during the
    execution.
    :raises Exception: For any other unexpected errors.

    :return: The new group object containing all set attributes.
    :rtype: Group
    """

    try:
        print('You are creating new group, that your friends can join further.')
        new_group_name = functions.get_non_empty_input('Give a name to your group: ')

        # new Group object
        new_group = classes.Group(new_group_name, userID)

        price_len = database.price_max_len

        new_group.price_limit = functions.get_non_empty_input("What is maximum price of gift? (don't set if you want to): ", None, max_length=price_len)
        new_group.place = functions.get_non_empty_input("Where gifts will be exchanged?: ")

        # receive information about timezone
        event_timezone = functions.timezone_declaration()

        # get information about date and time of meeting
        while True:
            meeting_date_str: str = input("\nWhen group will meet? ('YYYY-MM-DD hh:mm:ss'  24h format): ").strip()
            meeting_date = functions.get_offset_aware_datetime(meeting_date_str, event_timezone.zone)
            if meeting_date is None:
                print("Try again.")
                continue
            # eligible value:
            elif meeting_date > datetime.now(tz=timezone.utc):
                break
            else:
                print("You cannot input past date. Input an upcoming date.")
        new_group.meetingDate = meeting_date

        # get information about date and time of deadline for passing gift list
        while True:
            deadline_str: str = input("Final call date for users to input gift propositions ('YYYY-MM-DD hh:mm:ss'  24h format): ").strip()
            deadline = functions.get_offset_aware_datetime(deadline_str, event_timezone.zone)
            if deadline is None:
                print("Try again.")
                continue
            # eligible value:
            elif deadline > datetime.now(tz=timezone.utc):
                if deadline < meeting_date:
                    break
                else:
                    print("Typed in deadline is later than meeting date- input correct deadline.")
                    continue
            else:
                print("You cannot input past date. Input an upcoming date.")
        new_group.deadline = deadline
        new_group.tz = event_timezone.zone
        new_group.remarks = input("Any additional information for the group members: ")

        # saving Group object attributes
        cursor.execute(
            "INSERT INTO groups_table\
            (groupName, groupPIN, adminID, price_limit, place, meetingDate, deadline, eventTimezone, remarks, usersFinished)\
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (new_group.groupName, new_group.PIN, new_group.adminID, new_group.price_limit, new_group.place,
             new_group.meetingDate, new_group.deadline, new_group.tz, new_group.remarks, new_group.usersFinished))

        db_connection.commit()
        cursor.execute("SELECT groupID FROM groups_table WHERE groupName=%s", (new_group_name,))

        # assign new group number to class
        new_group.groupID = cursor.fetchone()[0]
        # add admin to group members table
        cursor.execute("INSERT INTO group_members (groupID, userID, groupName) VALUES (%s, %s, %s)",
                       (new_group.groupID, userID, new_group.groupName))
        db_connection.commit()
        return new_group

    except mysql.connector.Error:
        log_msg = ('Database error. Please input data formatted correctly.')
        logger_withDisplay.warning(log_msg)
        return set_group(userID)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return set_group(userID)


# PART 2: joining to group #############################################################################################
# Join a user to a group by verifying the group number and PIN
def join_to_group(userID: int):
    """
    Allows a user to join a group by validating the group number and PIN, and then adds the user to the group in the database.

    This function prompts the user to input a 9-digit group number, which is validated using `verify_group_number()`.
    If the group number is valid, it prompts the user to verify the group PIN using `verify_group_pin()`. Upon successful 
    verification of both, the user is added to the `group_members` table in the database. The user can also opt to exit the 
    process by entering 'x' at any time.

    :param userID: The ID of the user attempting to join a group.

    :raises IntegrityError: If a database integrity issue occurs during the insertion.
    :raises Exception: For any unexpected errors that may occur during execution.

    :return: 
        - If the user successfully joins a group, control is returned to the `my_groups()` function.
        - None is returned if the user opts to interrupt the process or if an error occurs.
    """


    while True:
        try:
            group_num_from_user_str = input("Input 9-digit group number that you want to join (input 'x' to interrupt and step back): ")
            if group_num_from_user_str.strip().lower() == 'x':
                break
            else:
                group_return = verify_group_number(userID, group_num_from_user_str)
                if group_return[0] is True:
                    group_num = group_return[1]
                    group_name = group_return[2]

                    while True:
                        PIN_return = verify_group_pin(group_num)
                        if PIN_return is True:
                            try:
                                cursor.execute("INSERT INTO group_members (groupID, userID, groupName) VALUES (%s, %s, %s)",
                                               (group_num, userID, group_name))
                                db_connection.commit()
                                print(f"You are successfully added to group {group_num}, {group_name}!")
                                return my_groups(userID)
                            except IntegrityError as err:
                                print("Database integrity error occurred")
                                logger.error(e, exc_info=True)
                                break
                            except Exception as e:
                                print(f"An unexpected error occurred.")
                                logger.error(e, exc_info=True)
                                break
                        elif PIN_return is False:
                            break
                        else:
                            continue
                else:
                    continue
        except ValueError as err:
            err_msg = f"Wrong value error: {err} "
            logger_withDisplay.warning(err_msg)
        except Exception as e:
            print(f"An unexpected error occurred.")
            logger.error(e, exc_info=True)


# Verifies if the provided group number exists in the database
def verify_group_number(userID: int, group_num_str: str):
    """
    Checks if a group with the provided number exists in the database.

    This function verifies the length and format of the provided group number,
    then queries the database to check if a group with that number exists.
    If the group exists, it returns the group number and name.

    :param userID: The ID of the user.
    :param group_num_str: The 9-digit group number to check.

    :return: A tuple (True, group_num, group_name) if the group exists, or (None, ) if it does not.
    :rtype: tuple
    """

    try:
        # check if length of group number is correct
        if len(group_num_str) != 9:
            log_msg = ("Invalid group number length.")
            logger_withDisplay.warning(log_msg)
            return (None, )

        group_num = int(group_num_str)

        # to check if user has been already added to this group
        cursor.execute("SELECT groupID FROM group_members WHERE userID = %s", (userID,))
        db_fetch = cursor.fetchall()
        group_list = [i[0] for i in db_fetch]
        if group_num in group_list:
            print("You have been already added to this group.")
            return (None, )
        else:
            # retrieving group name from db
            cursor.execute("SELECT groupName FROM groups_table WHERE groupID = %s", (group_num,))
            # condition fullfiled
            db_fetch = cursor.fetchone()
            if db_fetch:
                group_name = db_fetch[0]
                return True, group_num, group_name
            else:
                log_msg = ("Such group does not exist.")
                logger_withDisplay.warning(log_msg)
                return (None, )
    except ValueError as err:
        log_msg = (f"Wrong type: {err}")
        logger_withDisplay.warning(log_msg)
        return (None, )
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return (None, )


# Verifies if the provided PIN is correct
def verify_group_pin(groupID: int):
    """
    Verifies the group PIN provided by the user for accessing the group.

    This function prompts the user to enter a 6-digit PIN to verify their access to the specified group.
    It retrieves the correct PIN from the database and compares it with the user input. The user can
    cancel the process by typing 'x'. If the PIN matches, the function returns True. If the user cancels,
    the function returns False. The user can retry entering the PIN if it is incorrect or improperly formatted.

    :param groupID: The ID of the group the user is trying to access.

    :return:
        - True if the PIN is correct.
        - False if the user cancels the process by typing 'x'.
        - None in case of any unexpected errors.
    :rtype: Optional[bool]
    """


    while True:
        try:
            PIN_str = input("Type in PIN to access the group (input 'x' to cancel the process): ").strip().lower()

            if PIN_str == 'x':  # input cancellation
                return False

            if len(PIN_str) == 6:
                PIN = int(PIN_str)
                cursor.execute("SELECT groupPIN FROM groups_table WHERE groupID=%s", (groupID,))
                dbPIN = cursor.fetchone()[0]
                if PIN == dbPIN:
                    return True
                else:
                    print("PIN incorrect. Try again.")
            else:
                print("Incorrect length of PIN. Try again.")
        except ValueError as e:
            log_msg = (f"Incorrect value error: {e}")
            logger_withDisplay(log_msg)
        except Exception as e:
            print(f"An unexpected error occurred.")
            logger.error(e, exc_info=True)


# PART 3: My Groups operations: ########################################################################################
# Entering user groups section
def my_groups(userID: int):
    """
    Displays the groups where the user is either an admin or a member and allows the user to select a group for further operations.

    The function first fetches the groups from the database where the user is an admin, and then fetches groups where the user is a member.
    The groups are displayed, and the user can choose a group to see further details. If the user is not part of any group, they are prompted
    to create or join a group.

    :param userID: The ID of the user whose groups are being fetched.

    :raises ValueError: If the input group number is not a valid integer.
    :raises mysql.connector.Error: If there is an issue fetching data from the database.
    :raises Exception: For any unexpected errors during execution.

    :return: None
    """

    try:
        # searching groups where user is an admin
        cursor.execute("SELECT groupID, groupName FROM groups_table WHERE adminID=%s", (userID,))
        admin_groups = cursor.fetchall()

        # searching other groups where user is a member
        cursor.execute(
            """
            SELECT groupID, groupName FROM group_members 
            WHERE userID=%s AND groupID NOT IN 
            (SELECT groupID FROM groups_table WHERE adminID=%s)
            """,
            (userID, userID)
        )
        member_groups = cursor.fetchall()


    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
        return set_group(userID)

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return

    all_groups = [i[0] for i in admin_groups] + [j[0] for j in member_groups]

    print("\nYour Groups:")

    # displaying both admin groups and joined:
    if admin_groups and member_groups:
        print("Groups under your management:")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for group in admin_groups:
            print(f"{group[0]:<20}{group[1]:<20}")

        print("\nOther groups where you belong as a guest:")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for group in member_groups:
            print(f"{group[0]:<20}{group[1]:<20}")
    # displaying only admin groups:
    elif admin_groups:
        print("\nGroups under your management:")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for group in admin_groups:
            print(f"{group[0]:<20}{group[1]:<20}")
    # displaying only joined groups:
    elif member_groups:
        print("\nGroups that you have joined:\n")
        print(f"{'Group number:':<20}{'Group name:':<20}")
        for group in member_groups:
            print(f"{group[0]:<20}{group[1]:<20}")
    # no groups joined:
    else:
        print("You are not a member of any group yet. Set up new group or join to one if you received an invitation.")
        return

    # choosing the group number that user want to operate in
    while True:
        try:
            chosen_group = int(input("\nChoose the group number to see group details:\n"))
            if chosen_group in all_groups:
                break
            else:
                print("Group number not found. Please choose a valid group number.")
        except ValueError:
            log_msg = ("Incorrect value. Please enter a valid group number.")
            logger_withDisplay.warning(log_msg)
            return my_groups(userID)

    # entering group that user wants to operate in
    try:
        enter_the_group(userID, all_groups, chosen_group)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Enter the group function
def enter_the_group(userID: int, all_groups: list, chosen_group: int, recursion: bool = False):
    """
    Retrieves group information from the database, creates an instance of the Group class,
    and allows the user to view or modify their gift list in the selected group.

    This function verifies if the user is a member of the selected group by checking the list of groups they belong to.
    If the user is a member, it fetches the group data from the database, creates a Group object, and retrieves
    the list of group members and their nicknames. The function also checks if the user has already submitted a
    gift list for the group. Based on this, the user can view, edit, or add a gift list. The function can be called
    recursively to handle the case where the user adds a gift list after declining initially.

    :param userID: The ID of the user entering the group.
    :param all_groups: A list of group IDs the user is a member of.
    :param chosen_group: The ID of the group selected by the user.
    :param recursion: A flag to indicate whether the function is being called recursively after the user adds their gift list. Defaults to False.

    :raises ValueError: If the chosen group is not in the user's list of groups.
    :raises mysql.connector.Error: If a database error occurs while fetching group data.
    :raises Exception: For any other unexpected errors.

    :return: None
    """

    if chosen_group not in all_groups:
        print("You are not a member of chosen group.")
        return

    try:
        # querying for obtain group information data
        cursor.execute("SELECT * FROM groups_table WHERE groupID=%s", (chosen_group,))
        group_data = cursor.fetchone()    # fetching collected data as a tuple

        if not group_data:
            print("Group not found.")
            return

        # query to get group members list and their nicknames
        cursor.execute(
            """
            SELECT group_members.userID, users.userNick FROM group_members 
            JOIN users ON group_members.userID = users.userID 
            WHERE groupID = %s 
            ORDER BY group_members.userID;
            """,
            (chosen_group,)
        )
        db_fetch = cursor.fetchall()
        group_members = [member[0] for member in db_fetch]  # extract members IDs
        group_members_with_nicks = [member for member in db_fetch]  # both IDs and nicknames

        # creating an instance of the Group class and assigning values
        group_object = classes.Group(group_data[1], group_data[3])
        group_object.groupID = group_data[0]
        group_object.PIN = group_data[2]
        group_object.members = group_members
        group_object.price_limit = group_data[4]
        group_object.place = group_data[5]
        group_object.timezone = pytz.timezone(group_data[8])
        group_object.meetingDate = group_data[6].astimezone(tz=group_object.timezone)
        group_object.deadline = group_data[7].astimezone(tz=group_object.timezone)
        group_object.remarks = group_data[9]

        # fetching group admin's data from db
        cursor.execute(
            "SELECT userID, userNick FROM users WHERE userID = (SELECT adminID FROM groups_table WHERE groupID = %s)",
            (chosen_group,)
        )
        admin_data = cursor.fetchone()

        # displaying group information by calling relevant function
        if not recursion:
            group_info_display(admin_data, group_members_with_nicks, group_object)

        # now checks if user has already added list of gifts
        gifts_in = gifts_added_check(userID, group_object.groupID)

        # if list of gift is stated in the group - than user can see or edit it:

        if gifts_in[0] is True:
            group_operations(userID, group_object)
        # if list of gifts has not been stated - than user has to declare it:
        else:
            while True:
                prompt = "Do you want to add gift list now? (y/n): "
                add_now = input(prompt).strip().lower()
                if add_now == 'y':
                    add_gifts(userID, group_object.groupID, group_object.groupName, group_object.price_limit, editmode=False, edit_type=None)
                    return enter_the_group(userID, all_groups, chosen_group, recursion=True)
                elif add_now == "n":
                    break
                else:
                    print("Wrong input, please enter 'y' or 'n'.")
        return
    except mysql.connector.Error as err:
        log_msg = ("Database error")
        logger_withDisplay.error(log_msg, err, exc_info=True)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Function for displaying details of chosen group
def group_info_display(admin_data: tuple, group_members_with_nicks: list, group_object: classes.Group):
    """
    Displays information about the selected group, including the admin's details, group members, and event information.

    The function shows the group's admin (with user ID and nickname), lists the other group members excluding the admin,
    and displays key group event details such as the gift price limit, meeting place, meeting date, deadline for wishlist submission,
    and any additional remarks from the group manager.

    :param admin_data: A tuple containing the admin's user ID and nickname (userID, userNick).
    :param group_members_with_nicks: A list of tuples where each tuple contains a member's user ID and nickname.
    :param group_object: An instance of the Group class containing details such as group ID, meeting date, price limit, and more.

    :raises Exception: For any other unexpected errors.

    :return: None
    """

    try:
        # displaying admin info
        print(f"\nGroup {group_object.groupID} information:")
        print(f"Admin of this group is: {admin_data[1]} (#{admin_data[0]}), other members are:")

        # displaying group members (excluding admin)
        n = 1
        for member in group_members_with_nicks:
            if member[0] != admin_data[0]:  # skip admin in members list
                print(f"{n:>3}. {member[1]:<10}(#{member[0]})")
                n += 1
            else:
                pass

        # displaying additional group details:
        print(f"\nPrice limit for gift is: {group_object.price_limit}")
        print(f"Place of meeting: {group_object.place}")
        print(f"Date of meeting: {group_object.meetingDate.strftime('%Y-%m-%d %H:%M:%S UTC%:z')}")
        print(f"Last call for pushing wishlist: {group_object.deadline.strftime('%Y-%m-%d %H:%M:%S UTC%:z')}")
        print(f"Additional info from group manager: \n{group_object.remarks}\n")

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Checks if user has added the wishlist:
def gifts_added_check(userID: int, groupID: int):
    """
    Checks if the user has added any gifts to their wishlist for a specific group.

    This function queries the database to retrieve the user's wishlist (up to 3 gifts) for the specified group.
    It returns a tuple with a boolean indicating whether at least one gift has been added, and the list of gifts
    (if any). If no gifts have been added, it returns False with an empty or partial gift list.

    :param userID: The ID of the user whose wishlist is being checked.
    :param groupID: The ID of the group for which the wishlist is being checked.

    :return: A tuple where:
        - The first element is a boolean indicating if at least one gift is added (True/False).
        - The second element is the list of added gifts (up to 3 gifts) if any gifts are added, or an empty list if none are added.
    :rtype: tuple
    """

    try:
        # query for gift list from db
        cursor.execute("SELECT gift_1, gift_2, gift_3 FROM group_members WHERE groupID = %s AND userID = %s", (groupID, userID))
        db_fetch = cursor.fetchone()

        gift_list = [gft for gft in db_fetch]
        # loop for check how many wishes were added:
        gnum = 0  # number of gifts saved in db
        for gift in gift_list:
            if gift is None:
                pass
            else:
                gnum += 1
        if gnum == 0:
            print("Any wish was added to group.")
            return (False,)
        else:
            print(f"\nYou've got {gnum} gift saved in group." if gnum == 1 else f"You've got {gnum} gifts saved in group.")
            return (True, gift_list)
    except mysql.connector.Error as err:
        print(f"Database error.")
        logger.error(err, exc_info=True)
        return (False, )
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return (False, )


# Allows a user to add or edit gifts for the wishlist in a group
def add_gifts(userID: int, groupID: int, group_name: str, price_limit: str, editmode: bool = False, edit_type: Optional[Literal['a', 's']] = None):
    """
    Allows a user to add or edit gifts in the wishlist for a specific group.

    This function enables users to add up to 3 gifts to their wishlist. If in `editmode`, users can modify
    their previously added gifts or selectively edit them based on the `edit_type`. It also provides the option
    to interact with WishAI (Gemini API) to get gift suggestions.

    - In add mode (editmode=False), the user can add up to 3 new gifts.
    - In edit mode (editmode=True), the user can either add new gifts (`edit_type='a'`) or edit specific gifts
      (`edit_type='s'`).

    :param userID: The ID of the user adding or editing gifts.
    :param groupID: The ID of the group to which the gifts are being added or edited.
    :param group_name: The name of the group used when interacting with the WishAI for gift suggestions.
    :param price_limit: The price limit for the group, used when generating gift suggestions with WishAI.
    :param editmode: Determines if the function is in edit mode. Defaults to False (adding new gifts).
    :param edit_type: Specifies whether the user is adding new gifts ('a') or selectively editing existing ones ('s').
                      Must be None if not in edit mode.

    :return: True if gifts were successfully added or edited; False otherwise.
    :rtype: bool

    :raises ValueError: If 'editmode' is not a boolean or if 'edit_type' is invalid.
    :raises Exception: For any other unexpected errors during the gift addition or editing process.
    """

    try:
        # If editmode is False, edit_type must be None
        if not editmode:
            if edit_type is not None:
                raise ValueError("edit_type must be None when editmode is False")
        # If editmode is True, edit_type must be 'a' or 's'
        else:
            if edit_type not in ['a', 's']:
                raise ValueError("Invalid edit_type value. Choose either 'a' or 's' when editmode is True.")

        # assign correct prompt message based on the mode (add or edit giftlist)
        prompt = "Now think about your 3 wishes :)" if editmode is False else "Save again your wishes. One at least - three maximum."
        print(prompt)

        # WISHAI PLUG IN (Gemini API)
        # Info for running WishAI- AI bot for generate gift ideas.
        print("Hey! If you do not have an idea what to you could wish - you always can ask for help of WishAI- our gift ideas helper! ;)")
        # ask for running WishAI
        wish_n = 1
        while True:
            prompt_wishai = "Do you want to start a chat with WishAI? (y/n): " if wish_n == 1 else "Do you want to start WishAI again? (y/n): "
            wishai_run_decision = input(prompt_wishai).strip()
            if wishai_run_decision == "y":
                wish_n += 1
                wishAI = wishAI_Gemini_API.gemini_api(group_name, price_limit)
                if wishAI is False:
                    continue  # if prompts violate security settings then there is a possibility to ask again
                break
            elif wishai_run_decision == "n":
                break
            else:
                print("Wrong input. Try again.")

        gifts = []  # list to contain gift objects
        gifts_jsons = []  # list for containing serialized gift objects
        db_gifts_columns = ['gift_1', 'gift_2', 'gift_3']  # list of db column names where gifts are contained

        def single_gift_add(position: int, gifts: list, editmode: bool):
            """Helper function for add single gift to list"""
            name = input("Name of dream gift: ").strip()
            description = input("Description of your wish: ").strip()
            gift = classes.Gift(name, description)  # object setting
            gifts.append(gift)  # adding gift object to list
            if editmode:
                print(f"You have updated gift no. {position + 1}. name: {gift.name:<20}Gift description: {gift.description}")

        # new gift_list (or overwrite of full list)
        if not editmode or (editmode and edit_type == 'a'):
            def more_gifts_question():
                """Helper function that asks the user if she/he wants to add next gift to their wishlist in current group.

                This function repeatedly prompts the user for a 'yes' or 'no' answer to determine
                if they want to add another gift.
                It handles invalid input and ensures only valid responses ('y' or 'n') are accepted.

                :return True if the user wants to add another gift, otherwise - False.
                :rtype bool
                """

                while True:
                    proceed_ask = input("Do you want to add next gift proposition? (y/n): ").strip().lower()
                    if proceed_ask == 'y':
                        return True
                    elif proceed_ask == "n":
                        return False
                    else:
                        print("Wrong input- try again.")

            # loop for adding gifts (up to 3 gifts)
            for n in range(0, 3):
                if n > 0:  # condition to skip first turn
                    proceed = more_gifts_question()
                    if not proceed:
                        break
                single_gift_add(n, gifts, False)

        # editing existing giftlist one by one
        else:
            # fetching current gift list from db
            clause = ", ".join(db_gifts_columns)
            cursor.execute(f"SELECT {clause} FROM group_members WHERE groupID = %s AND userID = %s", (groupID, userID))
            db_fetch = cursor.fetchone()
            gift_list_json_pulled = [i for i in db_fetch]  # list with gifts in json format fetched from db

            # iterating trough fetched list
            for n, gift_json_pulled in enumerate(gift_list_json_pulled, start=0):
                if gift_json_pulled is not None:
                    gift_dict = json.loads(gift_list_json_pulled[n])  # retrieve dict from JSON
                    gift_object = classes.Gift(gift_dict['name'], gift_dict['description'])  # set instance of Gift class
                    print(f"Gift no. {n + 1}. name: {gift_object.name:<20}Gift description: {gift_object.description}")

                    # choosing the action that could be taken with this gift
                    prompt = "Press [y] to replace gift, [d] for delete or ENTER to keep this gift in wishlist: "
                    while True:
                        action = input(prompt).strip().lower()
                        if action == "":
                            gifts.append(gift_object)
                            break
                        elif action == 'd':
                            break
                        elif action == 'y':
                            single_gift_add(n, gifts, True)
                            break
                        else:
                            print("Incorrect input.")
                            continue

                # now case when current position of gift list is empty
                else:
                    prompt1 = f"\nGift no. {n + 1}. is empty. Do you want to set new wish? (y/n): "
                    action1 = input(prompt1).strip().lower()

                    if action1 == 'y':
                        single_gift_add(n, gifts, True)
                    elif action1 == 'n':
                        pass
                    else:
                        print("Incorrect input. Enter 'y' for yes or 'n' for no.")

            # check if the list is not empty. If yes- then starts add_gifts() function again to add at least one gift.
            if len(gifts) == 0:
                print("Your gift list is empty. Please set up at least one gift :) ")
                return add_gifts(userID, groupID, group_name, price_limit, editmode=True, edit_type='a')  # recursion of the function

        def db_gift_list_update(gifts: list, db_gifts_columns: list):
            """
            Helper function for update the user's gift list and the number of gifts in the database.

            This function takes the list of gifts provided by the user, serializes them into JSON format,
            and updates the corresponding columns in the 'group_members' table. It also updates the number of
            users who have submitted their gift lists for the group.

            :param gifts: A list of gift objects to be added or updated.
            :param db_gifts_columns: A list of column names in the database corresponding to the gift slots.
            :return: None
            """

            # printing added gift propositions
            print("\nYour current gift list:")
            for n, gift in enumerate(gifts, start=0):
                if gift is not None:
                    # displaying gift list with accurate formatting
                    print(f"{n + 1}. Gift name: {gift.name:<20}Gift description: {gift.description}")

            number_of_gifts = len(gifts)  # count of gift list length before adding empty positions

            # loop for adding empty positions to list
            while len(gifts) < len(db_gifts_columns):
                gifts.append(None)

            # loop for serialize objects as JSONs:
            n = 0
            for n in range(0, 3):
                if gifts[n] is not None:
                    gift_json = json.dumps(gifts[n].__dict__)  # serialize object attributes in JSON notation
                    gifts_jsons.append(gift_json)  # contain JSON in list
                else:
                    gifts_jsons.append(None)  # if object is None then insert empty position

            # preparing sql query
            set_clause = ", ".join([f"{db_gifts_columns[i]} = %s" for i in range(len(gifts))])
            sql_query = f"UPDATE group_members SET {set_clause} WHERE groupID = %s AND userID = %s;"
            params = gifts_jsons + [groupID, userID]
            cursor.execute(sql_query, params)

            # update number of gifts in db
            cursor.execute("UPDATE group_members SET number_of_gifts = %s WHERE groupID = %s AND userID = %s",
                           (number_of_gifts, groupID, userID))

            # increase the number of users that pushes gift list to group:
            if not editmode:
                # increase the number of users that pushes gift list to group:
                cursor.execute("UPDATE groups_table SET usersFinished = usersFinished + 1  WHERE groupID = %s;", (groupID,))

            # commit changes to the db
            db_connection.commit()
        db_gift_list_update(gifts, db_gifts_columns)

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Manages group-related operations based on user role (admin or regular member).
def group_operations(userID: int, group_object: classes.Group):
    """
    Handles the group operations, such as viewing or editing gift lists, running the gift mixer,
    and displaying the group PIN. Admin-specific options are included when the user is the group admin.

    :param userID: ID of the user interacting with the group.
    :param group_object: The Group object containing group details.
    """

    # determine if user is a group admin
    admin_mode = True if userID == group_object.adminID else False

    # group operations options
    while True:
        print("\nOPTIONS:")
        # displaying varies prompt in case user is admin or not.
        if admin_mode is True:
            print("[1] Preview gift list \n[2] Edit gift list \n[3] Run Gift Mixer! \n[4] Remind group PIN \n[e] Exit to Main Menu")
        else:
            print("[1] Preview gift list \n[2] Edit gift list \n[e] Exit to Main Menu")
        program_mode = input('\nChoose mode : ')

        if program_mode.strip() == '1':
            displaying_gift_list(userID, group_object)

        elif program_mode.strip() == '2':
            edit_gift_list(userID, group_object)

        elif program_mode.strip() == '3' and group_object.adminID == userID:  # option only for admins
            run_mixer(group_object)

        elif program_mode.strip() == '4' and group_object.adminID == userID:  # option only for admins:
            print(f"{group_object.groupName} group PIN is: {group_object.PIN}")

        elif program_mode.strip().lower() == 'e':  # exit
            return

        else:
            print("Wrong input. Choose correct option.\n")


# Fetches and displays the user's current gift list from the database.
def displaying_gift_list(userID: int, group_object: classes.Group):
    """
    Retrieves and displays the user's gift list from the database.
    Gifts are displayed with their name and description if available.

    :param userID: ID of the user whose gift list is to be displayed.
    :param group_object: The Group object containing group details.
    """

    try:
        print("\nYour wishes:")
        # fetching current gift list from db
        cursor.execute("SELECT gift_1, gift_2, gift_3 FROM group_members WHERE groupID = %s AND userID = %s",
                       (group_object.groupID, userID))
        db_fetch = cursor.fetchone()
        gifts_json_list = [i for i in db_fetch]

        # iterate trough json-gift list:
        for n, wish in enumerate(gifts_json_list, start=0):
            if wish is not None:
                gift_dict = json.loads(wish)  # retrieve dicts from json
                # set instance of Gift class
                gift_object = classes.Gift(gift_dict.get('name'), gift_dict.get('description'))
                # displaying gift list with accurate formatting
                print(f"{n + 1}. Gift name: {gift_object.name:<20}Gift description: {gift_object.description}")
            else:
                pass

    except mysql.connector.Error as err:
        log_msg = ("Database error")
        logger_withDisplay.error(log_msg, err, exc_info=True)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Allows the user to edit their gift list if the deadline hasn't passed.
def edit_gift_list(userID: int, group_object: classes.Group):
    """
    Enables the user to modify their gift list. The user can either edit the entire list or individual items,
    provided the deadline for editing has not passed.

    :param userID: ID of the user editing the gift list.
    :param group_object: The Group object containing group details and the deadline.
    """

    try:
        # verify whether current datetime has passed the deadline
        current_dt = datetime.now(timezone.utc)  # current dt
        deadline = group_object.deadline  # deadline for chosen group
        # check if deadline is an offset-aware datetime
        if functions.is_aware(deadline) is True:
            pass
        else:
            deadline = functions.get_offset_aware_datetime(str(deadline), None)


        # compare current datetime and deadline
        if current_dt > deadline:
            print("Deadline has passed. You cannot edit you gift list.")
            return

        # giftlist edit section:
        print("Now you will edit your wishes.")
        while True:
            type_of_edit = input("\nPress [a] for change all gifts or [s] for change gifts one by one: ")

            # overwrite whole giftlist- runs add_gifts() in edit mode
            if type_of_edit.strip().lower() == 'a':
                add_gifts(userID, group_object.groupID, group_object.groupName, group_object.price_limit, editmode=True, edit_type='a')
                return

            # call for edit list one by one:
            elif type_of_edit.strip().lower() == 's':
                print("\nYou'll be changing gift in the wish list one by one.")
                add_gifts(userID, group_object.groupID, group_object.groupName, group_object.price_limit, editmode=True, edit_type='s')
                return
            else:
                print('Input incorrect.\nTry again.\n')

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return


# Assigns each user in the group to another user as part of a secret gift exchange, saving the results to the database.
def run_mixer(group_object: classes.Group):
    """
    Conducts the gift exchange mixer by randomly pairing users who submitted
    their gift lists. The function fetches wishlists, emails, and user data,
    assigns gift givers to receivers, updates the database, and sends emails
    with the results.

    :param group_object: The Group object containing group details and member information.
    """

    # prep.1: fetching usersID from selected group who passed wishlist
    query = "SELECT userID FROM group_members WHERE groupID = %s AND number_of_gifts > 0 ORDER BY userID;"
    cursor.execute(query, (group_object.groupID,))
    db_fetch = cursor.fetchall()
    giver_list = [i[0] for i in db_fetch]  # retrieving users id from db fetch

    # conditions to quit the function if less than 2 users passed their gift lists.
    if len(giver_list) == 0:
        print("Anyone passed the gift list. Input your gift list and brief the other ones to pass their gift lists and then run mixer once again.")
        return
    elif len(giver_list) == 1:
        print("You are the only member of this group who passed the gift list. Brief other group members to pass their gift lists and then run mixer once again.")
        return
    else:
        pass

    receiver_list = giver_list.copy()  # receiver_list = []  # list for contain userID to whom gift will be bought
    giceiver_pairs = []  # list for contain dicts {giver:receiver}
    giverData_objects_list = []  # list for contain giver data objects (ID, mail, nick, wishlist to buy)

    # prep. 2: pulling wishlists
    # query for fetching gift list from db
    query = f"SELECT userID, gift_1, gift_2, gift_3 FROM group_members WHERE groupID = %s AND number_of_gifts > 0 ORDER BY userID;"
    cursor.execute(query, (group_object.groupID,))
    db_fetch = cursor.fetchall()
    wishlists = {}  # dict for contain each user wishlist
    # loop for retrieving wishlists
    for row in db_fetch:
        key = row[0]
        values = []
        # fetch gift items from db table, drop nulls and unionize existing ones
        n = 1
        for n in range(1, 4):
            if row[n] is not None:
                unjsonized_value = json.loads(row[n])
                values.append(unjsonized_value)
        # creating dict {userID: wishlist}
        user_wishes = {key: values}
        wishlists.update(user_wishes)  # adding position to dictionary

    # prep. 3: fetching emails and nicknames from db for mailing
    query_list = ", ".join(str(ids) for ids in giver_list)
    query = f"SELECT userID, userNick, userMail  FROM users WHERE userID IN ({query_list}) ORDER BY userID;"
    cursor.execute(query)
    db_fetch = cursor.fetchall()
    mail_addresses = {}  # dict for contain IDs, nicknames and mails
    for position in db_fetch:
        pair = {position[0]: (position[1], position[2])}  # creating pair with ID and tuple (nickname and email of giver)
        mail_addresses.update(pair)  # adding pair do dict

    # START MIXER - creating pairs giver-receiver and giver-wishlist to buy

    # shuffle receiver list first, then pair giver with receiver
    random.shuffle(giver_list)
    # iterate trough givers and receivers lists to
    for giver in giver_list:
        if giver == receiver_list[0]:
            receiver_list.append(receiver_list.pop(0))
        receiver = receiver_list.pop(0)
        pass_pair = {giver: receiver}  # joining IDs into dictionary
        giver_nick = mail_addresses.get(giver)[0]
        giver_mail = mail_addresses.get(giver)[1]
        receiver_name = mail_addresses.get(receiver)[0]
        # setting instance of Giver_data class
        giverData_object = classes.GiverData(
            giver, giver_mail, giver_nick, receiver_name, group_object.groupName, wishlists.get(receiver))
        # append elements to lists:
        giceiver_pairs.append(pass_pair)
        giverData_objects_list.append(giverData_object)

    # pushing obtained lists to db:
    # 1. Passing giver-receiver list to groups_table:
    giceiver_pairs_json = json.dumps(giceiver_pairs)  # serialize object attributes in JSON notation
    query = f"UPDATE groups_table SET giver_receiver_pairs = %s WHERE groupID = %s"
    cursor.execute(query, (giceiver_pairs_json, group_object.groupID))
    db_connection.commit()

    # 2. Passing giver_data_object to db:
    # iterate trough user-objects to serialize each one as a json and push to db
    for gvr in giverData_objects_list:
        # set order of keys in class:
        gvr_ordered = gvr.to_ordered_dict()
        gvr_json = json.dumps(gvr_ordered)
        # preparing mysql statement:
        query = f"UPDATE group_members SET giver_object = %s WHERE groupID = %s AND userID = %s"
        params = (gvr_json, group_object.groupID, gvr.ID)
        cursor.execute(query, params)
        db_connection.commit()

    # Run mailing function
    mailing_from_main(group_object, giverData_objects_list)


# Sends personalized emails to each user participating in the gift exchange with details about their assigned recipient.
def mailing_from_main(group_object: classes.Group, giverData_list: list):
    """
    Sends personalized email notifications to each user in the group, informing them about their assigned gift recipient
    and providing the recipient's wishlist and other group details.

    :param group_object: The Group object containing group details, including meeting information and remarks.
    :param giverData_list: A list of GiverData objects, each containing information about the giver and their assigned recipient.
    """

    try:
        # iterate trough user-objects to send personalized mail to each one
        for giver in giverData_list:
            # subject setting
            subject = f"{giver.nick}, your GiftMixer {giver.groupName} group is ready! Prepare to be a real giver and choose gift for the other one! :) "

            # email body setting
            wshlst = giver.wishlist  # taking wishlist from object
            wishes_display = "\n"  # string to be put into mail
            # iterating trough wishes to add to string
            try:
                # for wish in wshlst:
                for index, wish in enumerate(wshlst, 0):
                    wish_name = wish.get("name")
                    wish_description = wish.get("description")
                    wishes_display = f"{wishes_display}{index+1}. Gift name: {wish_name}     Description: {wish_description} \n"
            except Exception as e:
                print(f"An unexpected error occurred.")
                logger.error(e, exc_info=True)

            # addition to body text with remark from group manager (if he/she passed it)
            body_addition = ""
            if group_object.remarks != "":
                body_addition += "Additional information for the group members: " + group_object.remarks

            # fetching group admin nick from db
            cursor.execute("SELECT userID, userNick FROM users WHERE userID = %s", (group_object.adminID,))
            admin_data = cursor.fetchall()[0]
            group_manager_id = admin_data[0]
            group_manager_nick = admin_data[1]

            # full body
            body = f"""Hi {giver.nick},\n\n{group_object.groupName} group has been completed and GiftMixer shuffled \
wishlists for you and your friends. Now you can fulfill {giver.receiverName} dream by buying one of the gifts from below wishlist:

{wishes_display}
Remember to not wait on the last call for buying gift- do it in advance! :) Price limit in {group_object.groupName} group is {group_object.price_limit}.

Your group meets on {group_object.meetingDate}.
Place of meeting is {group_object.place}.
{body_addition}
{group_object.groupName} group manager is {group_manager_nick} ({group_manager_id}).

Don't forget to sign the gift with receiver's nick name!

Thanks for using GiftMixer and have a lot fun with gift exchange! ;)
With \u2661 GiftMixer Team."""

            # run mailing function
            functions.send_email(giver.mail, subject, body)

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return


# PART 4: Profile settings #############################################################################################
# Manages profile settings, allowing users to change their nickname or password.
def profile_settings(userID: int, user_nick: str):
    """
    Allows users to modify their profile settings, such as changing their nickname or password.
    Provides an option to return to the main menu.

    :param userID: The ID of the user interacting with the profile settings.
    :param user_nick: The current nickname of the user.
    :return: The updated user nickname if changed, or the original nickname.
    :rtype: str
    """

    while True:
        print('\n[1] Change nick \n[2] Change password \n[b] Back to main menu')
        section_mode = input('Choose mode : ')

        if section_mode.strip().lower() == 'b':
            break

        elif section_mode.strip() == '1':   # nick edit
            new_user_nick = login.change_nick(userID, user_nick)
            # condition to step back if user nick hasn't been changed
            if new_user_nick is None:
                continue
            # else:
            #     user_nick = new_user_nick  # overwriting userNick variable
            return (new_user_nick, )

        elif section_mode.strip() == '2':    # password edit
            login.update_password(userID, user_nick)
        else:
            print("Wrong input. Try again.\n")


# MAIN MENU ############################################################################################################
# Displays the main menu and directs the user to the selected feature.
def main_menu():
    """
    Provides the main navigation menu for users to set a new group, join an existing group,
    manage their groups, update profile settings, or close the program.

    Options:
    - [1] Set a new group
    - [2] Join an existing group
    - [3] Manage user's groups
    - [4] Profile settings
    - [x] Close the program
    """

    while True:
        print('\n[1] Set new group \n[2] Join to group \n[3] My groups \n[4] Profile settings \n[x] Close program')
        program_mode = input('Choose mode : ')
        if program_mode.strip() == '1':    # starting new group
            set_group(userID)
        elif program_mode.strip() == '2':    # join to group
            join_to_group(userID)
        elif program_mode.strip() == '3':    # user group operations
            my_groups(userID)
        elif program_mode.strip() == '4':  # profile settings
            profile_settings(userID, user_nick)
        elif program_mode.strip().lower() == 'x':  # close program
            login.terminate_process()
        else:
            print("Wrong input. Try again.\n")


# condition to run main_menu function only it is run as main script
if __name__ == "__main__":
    try:
        # run the main program logic
        main_menu()
        pass
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
    finally:
        # ensure that the cursor and db connection will be closed in case of error occurs
        database.db_switch_off(db_connection, cursor)
