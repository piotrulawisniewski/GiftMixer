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
from mysql.connector import errorcode

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
        cursor.execute(f"UPDATE users SET userNick = '{new_Nick}' WHERE userID={userID}")
        db_connection.commit()
        print(f'Hi {new_Nick}')
        break
    except mysql.connector.IntegrityError as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            print('Chosen nick has been already occupied. Please choose another one.')
else:
    print(f'Hi {userNick},')

# setting User object:
UserObj = classes.User(userID)

# setting new group:
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
    newGroup.deadline = input("What is the last call date for others to input gift propositions (YYYY-MM-DD hh:mm:ss  24h format): ")
    newGroup.place = input("Where gifts will be placed/exchanged?: ")
    newGroup.remarks = input("Any additional information for the group members: ")

    # Saving object attributes
    cursor.execute(f"INSERT INTO groups_table(groupName, password, adminID, price_limit, deadline, place, remarks) \
    VALUES ('{newGroup.groupName}', '{newGroup.password}', '{newGroup.adminID}',\
    '{newGroup.price_limit}', '{newGroup.deadline}', '{newGroup.place}', '{newGroup.remarks}')  ")

    db_connection.commit()
    cursor.execute(f"SELECT groupID FROM groups_table WHERE groupName='{newGroup.groupName}'")
    newGroup.groupID = cursor.fetchone()[0]




def main_menu():

    while True:
        print('\n[1] Set new group \n[2] MyGroups \n[3] My Account')
        program_mode = input('Choose mode : ')
        if program_mode.strip() == '1':    # starting new group
            set_group(userID)
        # elif program_mode.strip() == '2':  # showing current groups
        #
        # elif program_mode.strip() == '3':  # Settings

        else:
            print("Wrong input- choose option 1, 2 or 3.\n")


if __name__ == "__main__":
    main_menu()




input('Press enter to continue...')






















