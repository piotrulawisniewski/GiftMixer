# Login section

import secrets
import string
import hashlib
import re
from getpass import getpass

user_details_filepath = 'users.txt'
special_characters = "!@#$%^&*()'\",./<>?{[]}"
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
        elif password.strip().upper() =='H':
            password = input(user_password_help_prompt)
        elif password.strip().upper() =='A':
            password = generate_password(default_password_lenght)
        else:
            print('Password incorrect.\nTry again.\n')
            password = input(user_password_help_prompt)
    return password

def set_password(passwd_provider):
    """FUNCTION: executes appropriate function depending on how user wants to set the password
        :param passwd_provider- A-automatic or U-by user
        :return password
        """

    if passwd_provider.strip().upper() == "A":
        passwd = generate_password(default_password_lenght) # launching auto-generate password function
    elif passwd_provider.strip().upper() == "U":
        passwd = user_input_password() # launching function for typing password by user
    return passwd


def hash_password(passwd):
    """FUNCTION: hashes a password using SHA-256 algorithm
            :param passwd_provider- A-automatic or U-by user
            :return password
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
    with open(user_details_filepath, "a") as f:
        f.write(f'{userMail} {hashed_passwd}\n')

    # change the saving user-details into "safe place"


def user_exists (userMail):
    """FUNCTION: function checks if user with a specific mail exists
                :param userMail
                :return T/F
                """
    try:
        with open(user_details_filepath, 'r') as f:
            for line in f:
                parts = line.split()
                if parts[0] == userMail:
                    return True
    except FileNotFoundError as fl_err:
        print(f'{fl_err.args[-1]}: {user_details_filepath}')
    return False


def authenticate_user(userMail, passwd):
    """FUNCTION: function checks if the specified password matches the hashed password stored in file/database
                :param userMail, password
                :return T/F
                """
    with open(user_details_filepath, 'r') as f:
        for line in f:
            parts = line.split()
            if parts[0] == userMail:
                hashed_passwd = parts[1]
                if hashed_passwd == hash_password(passwd):
                    return True
                else:
                    return False
    return False


def valid_email(address):
    """FUNCTION: checking if email is correct
           :param email adress
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
            print('e-mail incorrect. Please enter a valid email adress.')
        else:
            break

    if user_exists(userMail): # checks if account already exists
        print('User already exists.')
        return

    while True:  # prompt for check if user want to generate password or type in by own
        passwd_set_mode = input('Set password for your account. \nType [A] for auto-generate save password or [U] if you want to set password by yourself: ')
        if passwd_set_mode.strip().upper() in ['A', 'U']:
            break
        else:
            print('Choose [A] or [B].')

    passwd = set_password(passwd_set_mode) # launching chosen password input option

    hashed_passwd = hash_password(passwd)
    save_user(userMail, hashed_passwd)

    print('User account created successfully!')
    print('Your password is: ', passwd)


    """   
    [1] Future: replace checking if email is in database for sending 6 (or 8) digit code sent to mail.
    It is safer cause it never shows to third party if such account exists.  
      
    [2] Future: add activate link sent to mail while registering new user
    
    [3] Future: add password replace option- and sending first password to mail instead showing it in terminal.
    
    """

def login():
    """FUNCTION: user login function
           :param None
           :return None
           """

    userMail = input("Enter user e-mail: ")
    if not user_exists(userMail):
        print('User does not exist.')
        return
    else:
        while True:
            passwd = getpass("Password: ")
            if not authenticate_user(userMail, passwd):
                print("Password incorrect.")
            elif authenticate_user(userMail, passwd):
                break
        print('Log in passed!')












