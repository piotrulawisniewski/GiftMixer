#GiftMixer project
#R32NOR | ZOLCBYTERS
#2024

### FUNCTIONS ###
# all general purpose functions

# libs & modules


import json

import tzlocal
from datetime import datetime, timezone, tzinfo, timedelta
import zoneinfo


import pytz
import pendulum
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import configparser


local_timezone = tzlocal.get_localzone()
local_timezone_str = str(local_timezone)

# Local time Timestamp function for quick get current time for saving
def py_local_timestamp():
    """FUNCTION: use to return local time timestamp
       :param
       :return local timestamp
       """
    local_timezone = tzlocal.get_localzone()
    local_timestamp = datetime.now(local_timezone)
    return local_timestamp

# UTC time Timestamp function for quick get current UTC time for saving
def py_utc_timestamp():
    """FUNCTION: use to return UTC time timestamp
           :param
           :return utc timestamp
           """
    utc_timestamp = datetime.now(timezone.utc)
    return utc_timestamp





def get_local_timezone(timezone=None):

    # get the local timezone with tzlocal fe. Europe/Warsaw (for displaying purpose)
    local_timezone_str = tzlocal.get_localzone().key
    local_timezone = pytz.timezone(local_timezone_str)


    # get current local datetime (offset-aware)
    localtime = pendulum.now(local_timezone)

    # UTC offset get in seconds
    utc_offset_inseconds = localtime.utcoffset().total_seconds()
    # offset convert to hours:
    hours_offset = int(utc_offset_inseconds / 3600)
    minutes_offset = int((utc_offset_inseconds % 3600)/60)

    # formatting as "UTC+/-XX:YY"
    sign = "+" if hours_offset >= 0 else "-"
    tz_by_utc_offset = f"UTC{sign}{abs(hours_offset):02}:{abs(minutes_offset):02}"

    return local_timezone, tz_by_utc_offset

def timezone_details(timezone_str):

    timezone = pytz.timezone(timezone_str)
    timedoesntmatter = pendulum.now(timezone)

    # UTC offset get in seconds
    utc_offset_inseconds = timedoesntmatter.utcoffset().total_seconds()
    # offset convert to hours:
    hours_offset = int(utc_offset_inseconds / 3600)
    minutes_offset = int((utc_offset_inseconds % 3600)/60)

    # formatting as "UTC+/-XX:YY"
    sign = "+" if hours_offset >= 0 else "-"
    tz_by_utc_offset = f"UTC{sign}{abs(hours_offset):02}:{abs(minutes_offset):02}"

    return timezone, tz_by_utc_offset



def timezone_declaration():
    # timezone function call
    tz_infolist = get_local_timezone()
    timezone = tz_infolist[0]
    timezone_by_utc_offset = tz_infolist[1]

    print(f"\nNow you have to pass some information about date and time. Your timezone is {timezone} ({timezone_by_utc_offset}).\n")

    prompt = (f"\n- Press 'Enter' if you want to pass with the same timezone (suggested if your event takes place in your current timezone)\n\
- Input the name of other timezone fe. 'UTC' or 'Europe/Rome' (recommended if your event takes place in other timezone than yours or you share the group with international friends)\n\
- Press 'A' for displaying list of all possible timezones\n\
\nYour input: ")

    # checking user input:
    while True:
        tz_update_str = str(input(prompt)).strip()

        # pass with current timezone
        if tz_update_str == "":
            print(f"\nYou stay with timezone: {timezone} ({timezone_by_utc_offset}).\n")
            return timezone

        # display list of all possible timezones in pytz library
        elif tz_update_str.lower() == "a":
            all_timezones_display()
        # new timezone was inputted
        else:
            try:
                new_timezone = pytz.timezone(tz_update_str)
                ctist = datetime.now(new_timezone)  # current time in selected timezone
                ctist_display = ctist.strftime('%Y-%m-%d %H:%M:%S UTC%:z')  # formatting datetime
                print(f"current time in selected timezone: {ctist_display}")

                # formatting timezone like previously: <timezonename> (<UTC +00:00>)
                tz_infolist = timezone_details(new_timezone.zone)
                timezone = tz_infolist[0]
                timezone_by_utc_offset = tz_infolist[1]

                print(f"new timezone: {timezone} ({timezone_by_utc_offset})")
                return timezone

            except Exception:
                print("Incorrect input.")






















# timestamp = py_local_timestamp()
#
# print(timestamp)
# print(timestamp.tzinfo)
# print(timestamp.isoformat())

def all_timezones_display():

    allzones = pytz.all_timezones
    print(len(allzones))

    i = 1
    for zone in allzones:
        print(f"{i}. {zone}")
        i+=1




# function for fetch date

################################################################################


def get_offset_aware_datetime(user_input, timezone_str=None):
    """FUNCTION: Converts a user input string into an offset-aware datetime object.
       :param user_input (str): The datetime string provided by the user with required format
       :param timezone_str (str): if timezone name is not passed, then user current local timezone will be assigned
       :return aware_dt: An offset-aware datetime object.
       :return None: if user_input raises an ValueError.
       """

    timezone = pytz.timezone(tzlocal.get_localzone().key) if timezone_str == None else pytz.timezone(timezone_str)


    # Try to parse the input in different formats
    try:

        if len(user_input) == 19:  # Format YYYY-MM-DD HH:mm:ss
            naive_dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")
        elif len(user_input) == 16:  # Format YYYY-MM-DD HH:mm
            naive_dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
            naive_dt = naive_dt.replace(second=0)
        elif len(user_input) == 10:  # Format YYYY-MM-DD
            naive_dt = datetime.strptime(user_input, "%Y-%m-%d")
            naive_dt = naive_dt.replace(hour=0, minute=0, second=0)
        else:
            raise ValueError("Input format is not correct.")
    except ValueError as e:
        print(e)
        return None
    # Localize the naive datetime to the specified timezone
    aware_dt = timezone.localize(naive_dt)
    return aware_dt


def is_aware(dt):
    """FUNCTION: Check if datetime object is naive or aware
       :param dt (datetime object)
       :return True: if dt is aware
       :return False: if dt is naive
       """
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None




# # Example usage
# user_input_1 = "2024-07-09"
# user_input_2 = "2024-07-09 15:30"
# #timezone_str = 'America/New_York'
# # timezone_str = str(local_timezone)
#
#
#
#
#
#
# print(get_offset_aware_datetime(user_input_1, timezone_str))
# print(get_offset_aware_datetime(user_input_2, timezone_str))
# print(get_offset_aware_datetime(user_input_2, local_timezone_str))


# local_timezone = tzlocal.get_localzone()
# print(local_timezone)
# print(type(local_timezone))
#
# pytz_timezone = pytz.timezone(str(local_timezone))
# print(pytz_timezone)
# print(type(pytz_timezone))



# timezone1 = dt.timezone(offset=dt.timedelta(hours=-2))
# print(timezone1)




########################################################################



# Send email (one) function to push mails to users in the group
def send_email(recipient_email, subject, body):

    # pull data are in file under filepath: ~/config/ignored/config.ini, to cover sensitive data
    config_file_path = os.path.expanduser("config/ignored/config.ini")
    # parse the configuration file
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # pulling discreet data from config file

    host = config['email']['host']
    port = config['email']['port']
    sender_email = config['email']['sender_email']
    sender_name = config['email']['sender_name']
    sender_password = config['email']['sender_password']


    # Create email message
    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header(sender_name, 'utf-8')),sender_email))
    msg['To'] = recipient_email
    msg['Subject'] = Header(subject, 'utf-8') # encode the subject with UTF-8

    # email body
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        # connect to SMTP server
        server = smtplib.SMTP(host, port)
        server.starttls()  # connection encrypting

        # log into the STMP server
        server.login(sender_email, sender_password)

        # send email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("email sent successfully!")

        # disconnect from the SMTP server
        server.quit()

    except Exception as e:
        print(f"Error: {e}")

# Send many emails function (the same subject and body in each)
def send_emails_general(recipients_list, subject, body):

    # pull data are in file under filepath: ~/config/ignored/config.ini, to cover sensitive data
    config_file_path = os.path.expanduser("config/ignored/config.ini")
    # parse the configuration file
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # pulling discreet data from config file

    host = config['email']['host']
    port = config['email']['port']
    sender_email = config['email']['sender_email']
    sender_name = config['email']['sender_name']
    sender_password = config['email']['sender_password']

    # Create email message
    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header(sender_name, 'utf-8')),sender_email))
    msg['Subject'] = Header(subject, 'utf-8') # encode the subject with UTF-8

    # email body
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        # connect to SMTP server
        server = smtplib.SMTP(host, port)
        server.starttls()  # connection encrypting

        # log into the STMP server
        server.login(sender_email, sender_password)

        # iterating trough recipients list and sending emails:
        for recipient_email in recipients_list:
            msg['To'] = recipient_email
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Emails sent successfully!")

        # disconnect from the SMTP server
        server.quit()

    except Exception as e:
        print(f"Error: {e}")



# function that ensures that input will not be empty

def get_non_empty_input(prompt):
    while True:
        user_input = input(prompt)
        if user_input.strip():
            return user_input
        else:
            print("Input cannot be empty. Please try again.")





