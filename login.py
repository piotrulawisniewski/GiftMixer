# Login section

# libs & modules
import secrets
import string
import hashlib
import re
import os
import signal
import time
import configparser

import mysql.connector
from mysql.connector import errorcode
# import configparser
# import datetime
import sys

from getpass import getpass

# my modules:
import classes
import functions
import database

# connection to database:
database.database_creation()
db_connection = database.db_switch_on()
cursor = db_connection.cursor()
database.creating_tables(db_connection, cursor)


# pull data are in file under filepath: ~/config/ignored/config.ini, to cover sensitive data
config_file_path = os.path.expanduser("config/ignored/config.ini")
# parse the configuration file
config = configparser.ConfigParser()
config.read(config_file_path)


special_characters = "!@#$%^&*(),./<>?"
default_password_lenght = 16

def generate_password(length=16):
    """FUNCTION: auto-generate password
       :param length of password
       :return password
       """

    characters = string.ascii_letters + string.digits + special_characters  # scope of characters used to put into password
    while True:
        password = ''.join(secrets.choice(characters) for i in range(default_password_lenght))
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in special_characters for c in password)
        ):
            break
    return password

def user_input_password():
    """FUNCTION: password set by User
        :param None
        :return password
        """
    user_password_prompt = "\nInput own password (type [H] to see rules for password or [A] for auto-generate password) \nYour password: "
    user_password_help_prompt = "Password lenght must be between 8 and 16 characters.\nPassword needs to contain at least one: lowercase letter, uppercase letter, number, special character.\nYou can type 'A' for auto-generate password. \nYour password: "
    password = input(user_password_prompt)
    while True:
        if ( 8 <= len(password) <= 16
            and any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in special_characters for c in password)
        ):
            break
        elif password.strip().upper() == 'H':
            password = input(user_password_help_prompt)
        elif password.strip().upper() == 'A':
            password = generate_password(default_password_lenght)
        else:
            print('Password incorrect.\nTry again.\n')
            password = input(user_password_help_prompt)
    return password

def set_password(passwd_provide):
    """FUNCTION: executes appropriate function depending on how user wants to set the password
        :param passwd_provide- A-automatic or U-by user
        :return password
        """
    if passwd_provide.strip().upper() == "A":
        passwd = generate_password(default_password_lenght) # launching auto-generate password function
    elif passwd_provide.strip().upper() == "U":
        passwd = user_input_password() # launching function for typing password by user
    return passwd

def hash_password(passwd):
    """FUNCTION: hashes a password using SHA-256 algorithm
            :param passwd
            :return hashed password
            """
    passwd_bytes = passwd.encode('utf-8')
    hashed_passwd = hashlib.sha256(passwd_bytes).hexdigest()
    return hashed_passwd

"""
Add salt before hashing function:

import hashlib
import os

def generate_salt():
    # Generate a random salt using os.urandom() with 16 bytes (128 bits)
    return os.urandom(16)

def hash_password(password, salt):
    # Combine the password and salt
    salted_password = password.encode() + salt

    # Hash the salted password using SHA-256
    hashed_password = hashlib.sha256(salted_password).hexdigest()

    return hashed_password

def verify_password(hashed_password, stored_password, salt):
    # Hash the provided password with the stored salt
    new_hashed_password = hash_password(stored_password, salt)

    # Compare the new hash with the stored hashed password
    return hashed_password == new_hashed_password

# Example usage:
password = "MyPassword123"
salt = generate_salt()
hashed_password = hash_password(password, salt)

# Simulate storing the hashed password and salt in a database
stored_hashed_password = hashed_password
stored_salt = salt

# Simulate verifying a password
input_password = "MyPassword123"
if verify_password(stored_hashed_password, input_password, stored_salt):
    print("Password is correct!")
else:
    print("Password is incorrect!")
"""

def save_user(userMail, hashed_passwd):
    """FUNCTION: saves user login data to the users detail file
            :param userMail, hashed_passwd
            :return None
            """

# passing data to database
    cursor.execute("INSERT INTO users(userMail, created_at_pyTimestamp, modified_at_pyTimestamp, \
    UTC_created_at_pyTimestamp, UTC_modified_at_pyTimestamp ) VALUES (%s, %s, %s, %s, %s)", \
    (userMail, functions.py_local_timestamp(), functions.py_local_timestamp(), functions.py_utc_timestamp(), functions.py_utc_timestamp()))
    db_connection.commit()

# getting userID from users table
    cursor.execute("SELECT userID FROM users WHERE userMail = %s", (userMail,))
    idFromDB=cursor.fetchone()[0]

# passing data to passwords table
    if idFromDB:
        cursor.execute("INSERT INTO passwords (userID, userPassword, created_at_pyTimestamp, modified_at_pyTimestamp, UTC_created_at_pyTimestamp, UTC_modified_at_pyTimestamp)\
        VALUES (%s, %s, %s, %s, %s, %s)", \
        (idFromDB, hashed_passwd, functions.py_local_timestamp(), functions.py_local_timestamp(), functions.py_utc_timestamp(), functions.py_utc_timestamp()))

    else:
        print("This should never be displayed xD")

def user_exists (userMail):
    """FUNCTION: function checks if user with a specific mail exists
                :param userMail
                :return T/F
                """
    try:
        cursor.execute("SELECT userMail FROM users")
        db_fetch = cursor.fetchall()
        db_userMails = [row[0] for row in db_fetch]
        if userMail in db_userMails:
            return True
        else:
            return False
    except:
        print("You are our first user- please register first and invite your friends!")
    return False

def authenticate_user(userMail, passwd):
    """FUNCTION: function checks if the specified password matches the hashed password stored in file/database
                :param userMail, password
                :return T/F
                """

    cursor.execute("SELECT userPassword FROM passwords WHERE userID = \
                    (SELECT userID FROM users WHERE userMail = %s)", (userMail,))

    fetched_password = cursor.fetchone()[0]
    if fetched_password == hash_password(passwd):
        return True
    else:
        return False
    return False

def valid_email(address):
    """FUNCTION: checking if email is correct
           :param address
           :return boolean
           """
    valid_email_regex = r'^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$'
    if not re.search(valid_email_regex, address):
        return False
    return True

def register():
    """FUNCTION: new user registration
           :param None
           :return None
           """

    print('\nSet up new user.\n')
    while True:  # passes only email with correct syntax
        userMail = input('Your email: ')
        if valid_email(userMail) == False:
            print('e-mail incorrect. Please enter a valid email address.')
        else:
            break

    if user_exists(userMail): # checks if account already exists
        print('User already exists.')
        return

    while True:  # prompt for check if user want to generate password or type in by own
        passwd_prompt = input('Set password for your account. \nType [A] for auto-generated password or [U] if you want to set password by yourself: ')
        if passwd_prompt.strip().upper() in ['A', 'U']:
            break
        else:
            print('Choose [A] or [U].')

    passwd = set_password(passwd_prompt) # launching chosen password input option
    hashed_passwd = hash_password(passwd)
    save_user(userMail, hashed_passwd)

    print('User account created successfully!')
    print('Your password is: ', passwd)


def login():
    """FUNCTION: user login function
           :param None
           :return None
           """

    userMail = 'e@e.pl'#input("Enter user e-mail: ")
    if not user_exists(userMail):
        print('User does not exist.')
        return False
    else:
        while True:
            passwd = '7^B>?Jr(&>3ZLU%0'#getpass("Password: ")
            if not authenticate_user(userMail, passwd):
                print("Password incorrect.")
            elif authenticate_user(userMail, passwd):
                break
        print('\nLog in passed!')
        cursor.execute("SELECT userID FROM users WHERE userMail = %s", (userMail,))
        current_userID = cursor.fetchone()[0]
        return current_userID

def terminate_process():
    """FUNCTION: close running script
           :param None
           :return None
           """
    try:
        # goodbye phrase
        print("Thank you for using GiftMixer! See you soon! :)\nPlease invite your friends to our service!\nwww.giftmixer.eu")

        # Get the ID of the current process
        pid = os.getpid()

        # Try to terminate the process softly:
        os.kill(pid, signal.SIGTERM)

        # Wait 2 seconds to see if process terminates:
        time.sleep(2)

        # Check if the process is still running- kill the process if it is
        if os.path.exists(f"/proc/{pid}"):
            os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        print(f"No such process: {pid}")
    except PermissionError:
        print(f"Permission denied to terminate the process {pid}")
    except Exception as e:
        print(f"An error occured: {e}")

#  forgotten password reset

def forgotten_password():

    print("\nDon't worry- sometimes everyone forgot on something :)"
    "\nEnter email address associated with your account and we will send you instructions to reset your password.")

    # email validation
    while True:  # passes only email with correct syntax
        mailToReset = input("Your email address: ")
        if valid_email(mailToReset) == False:
            print('Sorry, it seems that you enter incorrect email. Please enter a valid email address.')
        else:
            break

    # fetching userID from db
    cursor.execute("SELECT userID FROM users WHERE userMail = %s", (mailToReset,))
    uID = cursor.fetchone()[0]

    # launching auto-generation of password
    passwd = set_password('A')
    hashed_passwd = hash_password(passwd)

    # passing updated password to db

    sql_query = "UPDATE passwords SET userPassword = %s, modified_at_pyTimestamp = %s, UTC_modified_at_pyTimestamp = %s WHERE userID = %s "
    params = (hashed_passwd, functions.py_local_timestamp(), functions.py_utc_timestamp(), uID)
    cursor.execute(sql_query, params)
    db_connection.commit()

    # mail parts
    subject = "GiftMixer password reset"
    body = f"""Hey, 
    
below you will find temporary password to your GiftMixer account. 
This is an auto-generated password- please change it after login 
at giftmixer.eu in 'Profile settings' tab.

Your temporary password:
{passwd}

Thanks for using GiftMixer!
With \u2661 GiftMixer Team."""

    # mail sending
    functions.send_email(mailToReset, subject, body)

    # final information
    ourMail = config['email']['sender_email']
    print(f"If your email address is saved in our database then you should receive email from us ({ourMail}) with instructions to reset your password."
          f"\nIf you cannot see email from us- please check your spam folder.")


    # REMARK: this is a first simple version of password reset script. \
    # Final version should not modify password in db when mail is passing. Link to password change should be sent in mail,
    # to prevent passwords from being maliciously changed without users awareness.



# main login/registration function:
def main_login():
    while True:
        print('\n[1] Sign in \n[2] Register \n[3] Forgotten password \n[x] Close program')
        program_mode = input('Choose mode: ')
        if program_mode.strip() == '1':    # login for existing users
            loginReturn = login()
            if loginReturn != False:
                return loginReturn
            # break

        elif program_mode.strip() == '2':  # register new user
            register() # launching register function

        elif program_mode.strip() == '3':  # forgotten password reset
              forgotten_password()

        elif program_mode.strip().lower() == 'x':  # exits the program
            try:
                database.db_switch_off(db_connection, cursor)
            finally:
                terminate_process()
            # break
        else:
            print("Wrong input- choose option 1, 2 or x.\n")

# RUN MAIN LOGIN
if __name__ == "__main__":
    main_login()



# other functions related to login/ profile stuff:


# Setting nick for the user (if unknown):
def set_user_nick(userID):

    try:
        cursor.execute(f"SELECT userNick FROM users WHERE userID=%s", (userID,))
        result = cursor.fetchone()
        userNick = result[0] if result else None

        if not userNick:
            while True:
                new_Nick = functions.get_non_empty_input("\nPlease set up an unique nick for your account: ")
                try:
                    cursor.execute("UPDATE users SET userNick = %s WHERE userID = %s", (new_Nick, userID))
                    db_connection.commit()
                    print(f'Hi {new_Nick},')
                    return new_Nick
                except mysql.connector.IntegrityError as err:
                    if err.errno == errorcode.ER_DUP_ENTRY:
                        print('Chosen nick has been already occupied. Please choose another one.')
                    else:
                        print(f"Database error: {err}")
        else:
            print(f'Hi {userNick},')
            return userNick

    # error handling for both- first assign and edit:
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# edit user nick:
def change_nick(userID, userNick):

    nn = 0
    while True:
        # Differentiate displaying phrase depends of iteration number:
        if nn == 0:
            changeNickDecision = input(f"{userNick}, do you want to change your nick? (y/n): ")
        else:
            changeNickDecision = input(f"Press 'y' for yes / 'n' for no: ")
        # check user desision:
        if changeNickDecision.strip().lower() == "y":
            try:
                changed_Nick = functions.get_non_empty_input("\nPlease input your new nick (remember that it has to be unique): ")

                try:
                    cursor.execute("UPDATE users SET userNick = %s WHERE userID = %s", (changed_Nick, userID))
                    db_connection.commit()
                    print(f'Ok, now your new nick is: {changed_Nick},')
                    return changed_Nick
                except mysql.connector.IntegrityError as err:
                    if err.errno == errorcode.ER_DUP_ENTRY:
                        print('Chosen nick has been already occupied. Please choose another one.')
                    else:
                        print(f"Database error: {err}")

            # error handling for both- first assign and edit:
            except mysql.connector.Error as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        # if user changed his/her mind then return None allow step back to submenu
        elif changeNickDecision.strip().lower() == "n":
            return None
        else:
            print("Wrong input.")
        nn += 1


# edit password:
def update_password(userID, userNick):

    nn = 0
    while True:
        # Differentiate displaying phrase depends of iteration number:
        if nn == 0:
            changePasswdDecision = input(f"{userNick}, do you want to change your password? (y/n): ")
        else:
            changePasswdDecision = input(f"Press 'y' for yes / 'n' for no: ")
        # check user decision:
        if changePasswdDecision.strip().lower() == "y":
            try:
                while True:  # prompt for check if user want to generate password or type in by own
                    passwd_prompt = input(
                        'Set new password for your account. \nType [A] for auto-generated password or [U] if you want to set password by yourself: ')
                    if passwd_prompt.strip().upper() in ['A', 'U']:
                        break
                    else:
                        print('Wrong input. Choose [A] or [U].')

                passwd = set_password(passwd_prompt)  # launching chosen password input option
                hashed_passwd = hash_password(passwd)

                # passing updated password to db

                sql_query = "UPDATE passwords SET userPassword = %s, modified_at_pyTimestamp = %s, UTC_modified_at_pyTimestamp = %s WHERE userID = %s "
                params = (hashed_passwd, functions.py_local_timestamp(), functions.py_utc_timestamp(), userID)
                cursor.execute(sql_query, params)
                db_connection.commit()

                print('Password changed successfully!')
                print('Your current password is: ', passwd)

            # error handling for both- first assign and edit:
            except mysql.connector.Error as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
            break
        # if user changed his/her mind then return None allow step back to submenu
        elif changePasswdDecision.strip().lower() == "n":
            return None
        else:
            print("Wrong input.")
        nn += 1














