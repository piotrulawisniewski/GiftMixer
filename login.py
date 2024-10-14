# GiftMixer project
# R32NOR | ZOLCBYTERS
# 2024

# Login section script

# libs & modules

import hashlib
import re
import os
import signal
import time
import configparser
import string
import secrets
import mysql.connector
from mysql.connector import errorcode, DataError
from getpass import getpass

# project scripts:
import functions
import database
from logger_config import logger, logger_withDisplay

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


# Function to auto-generate a secure password
def generate_password(length: int = 16):
    """Generates a random, secure password with a specified length.

    This function generates a password using a combination of uppercase and lowercase letters, digits, and special characters.
    It ensures the password meets security requirements by including at least one lowercase letter, one uppercase letter,
    one digit, and one special character.

    :param length: The length of the password to be generated. Defaults to 16 characters.

    :return: A randomly generated password.
    :rtype: str
    """

    # define the character set for the password: letters, digits, and special characters
    special_characters = "!@#$%^&*()_+"
    characters = string.ascii_letters + string.digits + special_characters
    try:
        while True:
            # generate a random password using the 'secrets' library for cryptographic security
            password = ''.join(secrets.choice(characters) for i in range(length))

            # ensure the password contains at least one lowercase, one uppercase, one digit, and one special character
            if (any(c.islower() for c in password)  # check for at least one lowercase letter
                    and any(c.isupper() for c in password)  # check for at least one uppercase letter
                    and any(c.isdigit() for c in password)  # check for at least one digit
                    and any(c in special_characters for c in password)  # check for at least one special character
            ):
                break  # break the loop once the password meets all the conditions

        return password
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Function to allow the user to set their own password
def user_input_password():
    """Prompts the user to input a password or auto-generate one.

    This function allows the user to input a password or opt for an auto-generated password. It checks if the user's input
    meets the required password rules, which include length between 8 and 48 characters, and the inclusion of at least one
    lowercase letter, one uppercase letter, one digit, and one special character.

    :return: A valid user-provided or auto-generated password.
    :rtype: str
    """

    # prompt the user to input their password or use special options
    user_password_prompt = "\nInput your own password (type [H] for password rules or [A] to auto-generate a password): \nYour password: "

    # prompt to show password rules if the user asks for help
    user_password_help_prompt = "Password length must be between 8 and 99 characters.\
\nPassword must contain at least one: lowercase letter, uppercase letter, number, and special character.\
\nYou can type 'A' to auto-generate a password.\
\nYour password: "

    special_characters = "!@#$%^&*()_+"

    # initial user password input
    password = input(user_password_prompt).strip()

    # loop until the password meets the requirements or is auto-generated
    while True:
        # check if the password meets all conditions
        if (8 <= len(password) <= 99
                and any(c.islower() for c in password)  # check for lowercase letter
                and any(c.isupper() for c in password)  # check for uppercase letter
                and any(c.isdigit() for c in password)  # check for digit
                and any(c in special_characters for c in password)  # check for special character
        ):
            break  # password is valid, exit the loop

        # if the user inputs 'H', show the password rules
        elif password.strip().upper() == 'H':
            password = input(user_password_help_prompt)

        # if the user inputs 'A', auto-generate a password
        elif password.strip().upper() == 'A':
            password = generate_password(17)  # assuming the default password length is 16
            break  # auto-generated password is always valid, so break the loop

        # if the password doesn't meet the conditions, ask the user to try again
        else:
            print("Password does not meet the requirements. Please try again.")
            password = input(user_password_help_prompt)

    return password


# Function that executes the appropriate password-setting method based on user input
def set_password(passwd_provide: str):
    """Determines how the password should be set (automatically or manually) based on user input.

    This function checks if the user wants to auto-generate the password or set it manually.
    Depending on the user's choice, it either calls the auto-generation function or prompts
    the user to input a password.

    :param passwd_provide: A string indicating the method ('A' for automatic, 'U' for user input).
    :return: The generated or user-provided password.
    :rtype: str
    """
    try:
        # check if user wants to auto-generate the password
        if passwd_provide.strip().upper() == "A":
            default_password_length = 16
            passwd = generate_password(default_password_length)  # auto-generate password

        # check if user wants to manually input the password
        elif passwd_provide.strip().upper() == "U":
            passwd = user_input_password()  # prompt user for password input

        return passwd

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Function to generate a random salt
def generate_salt():
    """Generates a random salt using os.urandom() with 16 bytes (128 bits).

    This function generates a secure, random salt that can be used in password hashing
    or other cryptographic functions. The salt is generated using the os.urandom()
    function, which provides 16 bytes of randomness (128 bits).

    :param None

    :return: A randomly generated salt.
    :rtype: bytes
    """
    return os.urandom(16)


# Function to hash a salted password using SHA-256 algorithm
def hash_password(passwd: str, salt: bytes):
    """Hashes the salted password using the SHA-256 algorithm.

    This function combines the provided password with the salt, then hashes
    the resulting string using the SHA-256 algorithm to ensure secure storage of passwords.

    :param passwd: The plaintext password to be hashed.
    :param salt: The salt to add to the password before hashing, ensuring uniqueness.

    :return: The resulting hashed password as a hexadecimal string.
    :rtype: str
    """
    try:
        # combine password and salt
        salted_passwd = passwd.encode('utf-8') + salt
        hashed_passwd = hashlib.sha256(salted_passwd).hexdigest()
        return hashed_passwd
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


def save_user(userMail: str, hashed_passwd: str, salt: bytes):
    """Saves user login data to the database.

    This function inserts the user's email and hashed password into the database. It also saves the salt used for hashing the password. The function assumes that a connection to the database and a cursor are already established.

    :param userMail: The email address of the user. This will be saved in the database and used for login.
    :param hashed_passwd: The hashed password of the user, which has been salted.
    :param salt: The salt used to hash the password.

    :raises IOError: If there is an error saving the data to the database.

    :return: None
    """
    try:
        # insert user email into users table
        cursor.execute(
            "INSERT INTO users (userMail, created_at_pyTimestamp_UTC, modified_at_pyTimestamp_UTC) VALUES (%s, %s, %s)",
            (userMail, functions.py_utc_timestamp(), functions.py_utc_timestamp())
        )
        db_connection.commit()

        # retrieve userID from users table
        cursor.execute("SELECT userID FROM users WHERE userMail = %s", (userMail,))
        idFromDB = cursor.fetchone()[0]

        # insert hashed password and salt into passwords table
        if idFromDB:
            cursor.execute(
                "INSERT INTO passwords (userID, userPassword, salt, created_at_pyTimestamp_UTC, modified_at_pyTimestamp_UTC) VALUES (%s, %s, %s, %s, %s)",
                (idFromDB, hashed_passwd, salt, functions.py_utc_timestamp(), functions.py_utc_timestamp())
                )
            db_connection.commit()
        else:
            print("User ID retrieval failed, which should not occur.")

    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
        return None
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Check if a user with the given email address exists in the database
def user_exists(userMail: str):
    """Checks if a user with the specified email address exists in the database.

    This function queries the database to check if there is an entry with the given email address in the `users` table.

    :param userMail: The email address to check for existence in the database.

    :return: True if the user exists, False otherwise.
    :rtype: bool

    :raises IOError: If there is an error querying the database.
    """
    try:
        cursor.execute("SELECT userMail FROM users WHERE userMail = %s", (userMail,))
        result = cursor.fetchone()
        return result is not None

    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
        return None
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Authenticate a user by comparing the provided password to the stored hashed password
def authenticate_user(userMail: str, passwd: str):
    """Authenticates a user by checking if the provided password matches the stored hashed password.

    This function retrieves the hashed password and salt for the user with the specified email address from the database.
    It then hashes the provided password with the retrieved salt and compares it to the stored hashed password.

    :param userMail: The email address of the user whose credentials are to be verified.
    :param passwd: The plaintext password provided by the user.

    :return: True if the provided password matches the stored hashed password, False otherwise.
    :rtype: bool

    :raises IOError: If there is an error querying the database.
    """
    try:
        cursor.execute(
            "SELECT userPassword, salt FROM passwords WHERE userID = (SELECT userID FROM users WHERE userMail = %s)",
            (userMail,)
            )
        db_fetch = cursor.fetchone()

        if db_fetch:
            fetched_hashed_password, fetched_salt = db_fetch

            # bypass if salt is None, use empty byte string
            if fetched_salt is None:
                fetched_salt = b''

            # compare provided password with stored hashed password
            if fetched_hashed_password == hash_password(passwd, fetched_salt):
                return True

        return False

    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
        return None
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Validate the format of an email address using a regular expression
def valid_email(address: str):
    """Check if the provided email address is valid.

    This function uses a regular expression to validate the format of an email address.
    It checks for a general pattern of a valid email address but may not cover all edge cases.

    :param address: The email address to be validated.

    :return: True if the email address is valid, False otherwise.
    :rtype: bool
    """
    valid_email_regex = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(valid_email_regex, address))


# Register a new user by validating email and setting a password
def register():
    """Register a new user by validating the email and setting a password.

    This function prompts the user to enter a valid email address and choose
    whether they want to provide their own password or have one auto-generated.
    It then saves the user data (email, hashed password, and salt) in the database.

    """
    try:
        print('\nSet up new user.\n')
        while True:  # passes only email with correct syntax
            userMail = input('Your email: ')
            if valid_email(userMail) is False:
                print('e-mail incorrect. Please enter a valid email address.')
            else:
                break

        if user_exists(userMail):  # checks if account already exists
            print('User already exists.')
            return

        while True:  # prompt for check if user want to generate password or type in by own
            passwd_prompt = input(
                'Set password for your account. \nType [A] for auto-generated password or [U] if you want to set password by yourself: ')
            if passwd_prompt.strip().upper() in ['A', 'U']:
                break
            else:
                print('Choose [A] or [U].')

        passwd = set_password(passwd_prompt)  # launching chosen password input option
        salt = generate_salt()
        hashed_passwd = hash_password(passwd, salt)
        save_user(userMail, hashed_passwd, salt)
        print('User account created successfully!')
        print('Your password is: ', passwd)

    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
        return None
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Login user by verifying email and password
def login():
    """Log in a user by verifying email and password.

    This function prompts the user for their email and password. If the email
    does not exist or the password is incorrect, it will notify the user.
    Once authenticated, the user is logged in and their user ID is returned.

    :param None

    :return current_userID: The user's unique ID if login is successful.
    :rtype: int
    """

    try:
        userMail = 'c@c.pl'  # 'b@b.pl'  # input("Enter user e-mail: ").strip()
        if not user_exists(userMail):
            print('User does not exist.')
            return False
        else:
            while True:
                passwd = 'GiX2XV^uQX5mY7qx'  # 'KbA+g0EJkc&i#_8H'  # getpass("Password: ").strip()
                if not authenticate_user(userMail, passwd):
                    print("Password incorrect.")
                elif authenticate_user(userMail, passwd):
                    break
            print('\nLog in passed!')
            cursor.execute("SELECT userID FROM users WHERE userMail = %s", (userMail,))
            current_userID = cursor.fetchone()[0]
            return current_userID

    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
        return None
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None


# Terminate the current running process gracefully or forcefully if necessary
def terminate_process():
    """Terminate the current running script gracefully or forcefully if necessary.

    This function attempts to terminate the running process softly using `SIGTERM`. If the process does
    not stop within 2 seconds, it will forcefully terminate it using `SIGKILL`. It also prints a
    goodbye message to the user.

    :param None
    :return None
    """

    try:
        # goodbye phrase
        print(
            "Thank you for using GiftMixer! See you soon! :)\nPlease invite your friends to our service!\nwww.giftmixer.eu")

        # get the ID of the current process
        pid = os.getpid()

        # try to terminate the process softly:
        os.kill(pid, signal.SIGTERM)

        # wait 2 seconds to see if process terminates:
        time.sleep(2)

        # check if the process is still running (kill the process if it is)
        if os.path.exists(f"/proc/{pid}"):
            os.kill(pid, signal.SIGKILL)

    except ProcessLookupError:
        log_msg = (f"No such process: {pid}")
        logger_withDisplay.warning(log_msg)
        raise
    except PermissionError:
        log_msg = (f"Permission denied to terminate the process {pid}")
        logger_withDisplay.warning(log_msg)
        raise
    except OSError:
        log_msg = (f"System error trying quit the process {pid}")
        logger_withDisplay.warning(log_msg)
        raise
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        raise


# Function to handle password reset requests for users
def forgotten_password():
    """Handle the process of resetting a forgotten password.

    This function prompts the user for their email address, validates it, and checks if the user exists in the database.
    If the user is found, an auto-generated temporary password is created, updated in the database,
    and sent to the user's email with instructions for resetting their password.

    :param None
    :return None
    """

    try:
        print("\nDon't worry- sometimes everyone forgot on something :)"
              "\nEnter email address associated with your account and we will send you instructions to reset your password.")

        # email validation
        while True:  # passes only email with correct syntax
            mailToReset = input("Your email address: ")
            if valid_email(mailToReset) is False:
                print('Sorry, it seems that you enter incorrect email. Please enter a valid email address.')
            else:
                break

        # fetching userID from db
        try:
            cursor.execute("SELECT userID FROM users WHERE userMail = %s", (mailToReset,))
            uID = cursor.fetchone()[0]
        except IndexError:
            log_msg = ("Such email doesn't exist in database.")
            logger_withDisplay.warning(log_msg)
            raise DataError

        # launching auto-generation of password
        passwd = set_password('A')
        salt = generate_salt()
        hashed_passwd = hash_password(passwd, salt)

        # passing updated password to db

        sql_query = "UPDATE passwords SET userPassword = %s, modified_at_pyTimestamp_UTC = %s WHERE userID = %s "
        params = (hashed_passwd, functions.py_utc_timestamp(), uID)
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
        print(f"If your email address is saved in our database then you should receive email from us\
({ourMail}) with instructions to reset your password. \nIf you cannot see email from us- please check your spam folder.")

    except DataError:
        log_msg = ('Wrong input.')
        logger_withDisplay.warning(log_msg)

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)

    # REMARK: this is a first simple version of password reset script. \
    # final version should not modify password in db when mail is passing. Link to password change should be sent in mail,
    # to prevent passwords from being maliciously changed without users awareness.
    # TO BE UPDATED...


# Main function for user login, registration, and password recovery
def main_login():
    """Handle the main login process for users.

    This function provides a menu for users to sign in, register a new account, reset a forgotten password,
    or exit the program. Based on the user's input, it triggers the appropriate function (login, register,
    forgotten_password, or terminate_process).

    :param None
    :return loginReturn: User ID after successful login or None if program is closed
    """
    while True:
        print('\n[1] Sign in \n[2] Register \n[3] Forgotten password \n[x] Close program')
        program_mode = input('Choose mode: ')

        if program_mode.strip() == '1':  # login for existing users
            loginReturn = login()
            if loginReturn is not False:
                return loginReturn

        elif program_mode.strip() == '2':  # register new user
            register()  # launching register function

        elif program_mode.strip() == '3':  # forgotten password reset
            forgotten_password()

        elif program_mode.strip().lower() == 'x':  # exits the program
            try:
                database.db_switch_off(db_connection, cursor)
            finally:
                terminate_process()

        else:
            print("Wrong input- choose option 1, 2 or x.\n")


# RUN MAIN LOGIN
if __name__ == "__main__":
    try:
        # run the main login logic
        main_login()
        pass
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
    finally:
        # ensure that the cursor and db connection will be closed in case of error occurs
        database.db_switch_off(db_connection, cursor)


# >>>>>Other functions related to login/ account stuff<<<<<


# Setting a user nickname if unknown
def set_user_nick(userID: int):
    """Assign a unique nickname for a user.

    This function checks if the user already has a nickname. If not, it prompts the user to set a unique
    nickname, ensuring it is not already in use in the database. Once set, the nickname is saved and returned.

    :param userID: ID of the user whose nickname needs to be set

    :return userNick: The newly set or existing nickname
    :rtype userNick: str

    :raises mysql.connector.Error: If there are database errors, including integrity issues.
    :raises Exception: For any other unexpected errors.
    """

    try:
        cursor.execute(f"SELECT userNick FROM users WHERE userID=%s", (userID,))
        result = cursor.fetchone()
        userNick = result[0] if result else None

        if not userNick:
            while True:
                new_Nick = functions.get_non_empty_input("\nPlease set up an unique nick for your account: ")
                try:
                    cursor.execute("UPDATE users SET userNick = %s WHERE userID = %s",
                                   (new_Nick, userID))
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

    # error handling for both - first assign and edit:
    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Change user's nickname
def change_nick(userID: int, userNick: str):
    """Allow a user to change their existing nickname.

    This function prompts the user to decide whether they want to change their nickname. If they choose 'yes',
    it ensures the new nickname is unique before updating it in the database. It handles database integrity
    errors in case of duplicate nicknames and other unexpected errors.

    :param userID: ID of the user whose nickname will be changed
    :param userNick: The current nickname of the user

    :return changed_Nick: The updated nickname if successfully changed, None if unchanged
    :rtype changed_Nick: str or bool (None)

    :raises mysql.connector.Error: If there are database-related issues, including integrity errors.
    :raises Exception: For any other unexpected errors.
    """
    try:
        nn = 0
        while True:
            # differentiate displaying phrase depends on iteration number:
            if nn == 0:
                changeNickDecision = input(f"{userNick}, do you want to change your nick? (y/n): ")
            else:
                changeNickDecision = input(f"Press 'y' for yes / 'n' for no: ")
            # check user decision:
            if changeNickDecision.strip().lower() == "y":
                try:
                    changed_Nick = functions.get_non_empty_input(
                        "\nPlease input your new nick (remember that it has to be unique): ")
                    cursor.execute("UPDATE users SET userNick = %s WHERE userID = %s", (changed_Nick, userID))
                    db_connection.commit()
                    print(f'Ok, now your new nick is: {changed_Nick},')
                    return changed_Nick
                except mysql.connector.IntegrityError as err:
                    if err.errno == errorcode.ER_DUP_ENTRY:
                        log_msg = ('Chosen nick has been already occupied. Please choose another one.')
                        logger_withDisplay.warning(err, exc_info=True)
                    else:
                        log_msg = (f"Database integrity error.")
                        logger_withDisplay.warning(err, exc_info=True)
                except mysql.connector.Error as err:
                    print('Database error.')
                    logger.warning(err, exc_info=True)
                except Exception as e:
                    print(f"An unexpected error occurred.")
                    logger.error(e, exc_info=True)

            # if user changed his/her mind then return None allow step back to submenu
            elif changeNickDecision.strip().lower() == "n":
                return None
            else:
                print("Wrong input.")
            nn += 1
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Change user's password
def update_password(userID: int, userNick: str):
    """Allow a user to change their existing password.

    This function prompts the user to decide whether they want to change their password.
    The user can choose between setting their own password or opting for an auto-generated one.
    The new password is then hashed with a new salt and updated in the database.

    :param userID: ID of the user whose password will be changed
    :param userNick: The current nickname of the user (used in personalized prompts)

    :return None: Returns None if the user declines to change the password

    :raises mysql.connector.Error: If there are database-related issues.
    :raises Exception: For any other unexpected errors.
    """
    try:
        nn = 0
        while True:
            # differentiate displaying phrase depends on iteration number:
            if nn == 0:
                changePasswdDecision = input(f"{userNick}, do you want to change your password? (y/n): ")
            else:
                changePasswdDecision = input(f"Press 'y' for yes / 'n' for no: ")
            # check user decision:
            if changePasswdDecision.strip().lower() == "y":
                try:
                    while True:  # prompt for check if user want to generate password or type in by own
                        passwd_prompt = input('Set new password for your account. \nType [A] for auto-generated\
password or [U] if you want to set password by yourself: ')
                        if passwd_prompt.strip().upper() in ['A', 'U']:
                            break
                        else:
                            print('Wrong input. Choose [A] or [U].')

                    new_passwd = set_password(passwd_prompt)  # launching chosen password input option
                    new_salt = generate_salt()
                    hashed_passwd = hash_password(new_passwd, new_salt)

                    # passing updated password to db

                    sql_query = "UPDATE passwords SET userPassword = %s, salt =%s, modified_at_pyTimestamp_UTC = %s WHERE userID = %s "
                    params = (hashed_passwd, new_salt, functions.py_utc_timestamp(), userID)
                    cursor.execute(sql_query, params)
                    db_connection.commit()

                    print('Password changed successfully!')
                    print('Your current password is: ', new_passwd)

                except mysql.connector.Error:
                    log_msg = ('Database error.')
                    logger_withDisplay.warning(log_msg)
                break
            # if user changed his/her mind then return None allow step back to submenu
            elif changePasswdDecision.strip().lower() == "n":
                return None
            else:
                print("Wrong input.")
            nn += 1
        # now exit program and log in with new password
        print(f"Your new password is: {new_passwd}. Now program will be closed, and you could log in with new password")
        try:
            database.db_switch_off(db_connection, cursor)
        finally:
            terminate_process()
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
