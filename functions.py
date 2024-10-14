# GiftMixer project
# R32NOR | ZOLCBYTERS
# 2024

# all general purpose functions

# libs & modules
import tzlocal
from datetime import datetime, timezone
import pytz
import pendulum
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import configparser

from logger_config import logger, logger_withDisplay


# local_timezone = tzlocal.get_localzone()
# local_timezone_str = str(local_timezone)


# local time Timestamp function for quick get current time for saving
def py_local_timestamp():
    """Returns the current local datetime with timezone information.

    This function retrieves the current local time, including the timezone, based on the user's system settings.

    :return: The current local time with timezone information.
    :rtype: datetime.datetime
    """
    local_timezone = tzlocal.get_localzone()
    local_timestamp = datetime.now(local_timezone)
    return local_timestamp


# UTC time Timestamp function for quick get current UTC time for saving
def py_utc_timestamp():
    """Returns the current UTC datetime.

    This function retrieves the current time in UTC, using the timezone-aware UTC datetime.

    :return: The current time in UTC.
    :rtype: datetime.datetime
    """

    utc_timestamp = datetime.now(timezone.utc)
    return utc_timestamp


def get_local_timezone():
    """Retrieves the local timezone and its UTC offset in a formatted string.

    This function determines the local timezone using `tzlocal` and formats the UTC offset in the "UTC+/-XX:YY" format. The offset is calculated in hours and minutes from the local time.

    :return: A tuple containing:
        - The local timezone object.
        - A string representing the UTC offset in "UTC+/-XX:YY" format.
    :rtype: tuple (pytz.timezone, str)
    """

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


def timezone_details(timezone_str: str):
    """Retrieves timezone details and its UTC offset for a given timezone.

    This function takes a timezone string, retrieves the corresponding timezone object, and calculates its UTC offset in hours and minutes. The offset is returned in the format "UTC+/-XX:YY".

    :param timezone_str: The string representing the timezone (e.g., 'Europe/Warsaw').
    :return: A tuple containing:
        - The timezone object corresponding to the given string.
        - A string representing the UTC offset in "UTC+/-XX:YY" format.
    :rtype: tuple (pytz.timezone, str)
    """
    # create timezone object
    timezone_obj = pytz.timezone(timezone_str)
    time_doesnt_matter = pendulum.now(timezone_obj)

    # UTC offset get in seconds
    utc_offset_inseconds = time_doesnt_matter.utcoffset().total_seconds()
    # offset convert to hours:
    hours_offset = int(utc_offset_inseconds / 3600)
    minutes_offset = int((utc_offset_inseconds % 3600)/60)

    # formatting as "UTC+/-XX:YY"
    sign = "+" if hours_offset >= 0 else "-"
    tz_by_utc_offset = f"UTC{sign}{abs(hours_offset):02}:{abs(minutes_offset):02}"

    return timezone_obj, tz_by_utc_offset


# prompts the user to confirm or set their event timezone
def timezone_declaration():
    """Prompts the user to specify or confirm their event timezone.

    This function retrieves the current local timezone and its UTC offset, then prompts the user to either:
    - Confirm the current timezone.
    - Input a different timezone.
    - Display a list of all available timezones.

    If the user inputs a valid timezone, the function displays the current time in that timezone and updates the event timezone information accordingly.
    If the user input is invalid, an error message is shown.

    :return: The timezone object corresponding to the user's selected or confirmed timezone.
    :rtype: pytz.timezone
    """

    # local timezone function call
    try:
        tz_infolist = get_local_timezone()
        event_timezone = tz_infolist[0]
        timezone_by_utc_offset = tz_infolist[1]
    except IndexError as err:
        log_msg = (f"System couldn't get your current timezone: {err}")
        logger_withDisplay.error(log_msg)
        return None
    except Exception as e:
        print("Unexpected error.")
        logger.error(e, exc_info=True)
        return None

    print(f"\nNow you have to pass some information about date and time. Your timezone is {event_timezone} ({timezone_by_utc_offset}).\n")

    prompt = (f"\n- Press 'Enter' if you want to pass with the same timezone (suggested if your event takes place in your current timezone)\n\
- Input the name of other timezone fe. 'UTC' or 'Europe/Rome' (recommended if your event takes place in other timezone than yours or you share the group with international friends)\n\
- Press 'A' for displaying list of all possible timezones\n\
\nYour input: ")

    # checking user input:
    while True:
        tz_update_str = str(input(prompt)).strip()

        # pass with current timezone
        if tz_update_str == "":
            print(f"\nYou stay with timezone: {event_timezone} ({timezone_by_utc_offset}).\n")
            return event_timezone

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

                # formatting <timezonename> as <UTC +00:00>
                tz_infolist = timezone_details(new_timezone.zone)
                event_timezone = tz_infolist[0]
                timezone_by_utc_offset = tz_infolist[1]

                print(f"Event timezone: {event_timezone} ({timezone_by_utc_offset})")
                return event_timezone

            except TypeError:
                log_msg = (f"Incorrect type inputted passed.")
                logger_withDisplay.warning(log_msg)
                return None
            except ValueError:
                log_msg = (f"Wrong input. Such timezone {tz_update_str} doesn't exists. ")
                logger_withDisplay.warning(log_msg)
                return None
            except Exception as e:
                print("Unexpected error.")
                logger_withDisplay.error(e, exc_info=True)
                return None


# display all possible timezones as numbered list
def all_timezones_display():
    """Displays a list of all available timezones nicely (with index numbers).

    This function retrieves and prints all timezones from the `pytz` library.
    It first prints the total number of timezones and then lists each timezone with an index number.

    :return: None
    """

    allzones = pytz.all_timezones
    print(len(allzones))
    i = 1
    for zone in allzones:
        print(f"{i}. {zone}")
        i += 1


# convert naive datetime into offset-aware dt
def get_offset_aware_datetime(user_input: str, timezone_str: str = None):
    """Converts a user input string into an offset-aware datetime object.

    This function parses a date-time string into a naive datetime object, and then localizes it to a specified timezone \
    or the user's local timezone if none is provided. \
    If the input format doesn't match these, a ValueError is raised.

    :param user_input: The datetime string provided by the user. Expected formats include:
        - 'YYYY-MM-DD HH:mm:ss'
        - 'YYYY-MM-DD HH:mm'
        - 'YYYY-MM-DD'
    :param timezone_str: A string representing the timezone name. If not provided, the user's current local timezone will be used.
    :return: An offset-aware datetime object localized to the specified timezone and converted to UTC.
    :rtype: datetime.datetime
    :return: None if the input format is incorrect or raises a ValueError.
    :rtype: None
    """

    # checks selected timezone
    timezone_chosen = pytz.timezone(tzlocal.get_localzone().key) if timezone_str is None else pytz.timezone(timezone_str)

    # try to parse the input in different formats
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
        log_msg = (f"Incorrect value error: {e}")
        logger_withDisplay.warning(log_msg)
        return None
    # localize the naive datetime to the specified timezone
    aware_dt = timezone_chosen.localize(naive_dt)
    aware_dt_utc = aware_dt.astimezone(timezone.utc)
    return aware_dt_utc


# function for check if dt object is offset-aware
def is_aware(dt: datetime):
    """Checks if a datetime object is timezone-aware.

    This function determines whether the provided datetime object has timezone information, indicating that it is timezone-aware.
    It returns `True` if the datetime object is aware and `False` if it is naive (lacking timezone information).

    :param dt: The datetime object to check.
    :return: `True` if the datetime object is timezone-aware, otherwise `False`.
    :rtype: bool
    """

    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


# function for sending a single email to a specified recipient
def send_email(recipient_email: str, subject: str, body: str):
    """Sends an email to a single recipient with the specified subject and body.

    This function reads email configuration details from a file,
    creates an email message with the given subject and body, and sends it to the specified recipient.
    The SMTP server connection is established and encrypted, and the function handles login and sending of the email.

    :param recipient_email: The email address of the recipient.
    :param subject: The subject of the email.
    :param body: The body content of the email.

    :return: None
    :raises Exception: Prints an error message if any exception occurs during the process.
    """

    # pull data are in file under filepath: ~/config/ignored/config.ini, to cover sensitive data
    config_file_path = os.path.expanduser("config/ignored/config.ini")
    # parse the configuration file
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # retrieve email settings from the config file
    host = config['email']['host']
    port = config['email']['port']
    sender_email = config['email']['sender_email']
    sender_name = config['email']['sender_name']
    sender_password = config['email']['sender_password']

    # create email message
    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header(sender_name, 'utf-8')), sender_email))
    msg['To'] = recipient_email
    msg['Subject'] = Header(subject, 'utf-8')  # encode the subject with UTF-8

    # attach email body
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
        print(f"Error. Unnable to connect server.")
        logger.error(e, exc_info=True)


# send many emails function (with the same subject and body in each)
def send_emails_general(recipients_list: list, subject: str, body: str):
    """Sends an email with a specified subject and body to a list of recipients.

    This function reads email configuration details from a file, creates an email message with the provided subject and body,
    and sends it to each recipient in the provided list.
    The SMTP server connection is established and encrypted, and the function handles login and sending of emails.

    :param recipients_list: A list of recipient email addresses.
    :param subject: The subject of the email.
    :param body: The body content of the email.

    :return: None
    :raises Exception: Prints an error message if any exception occurs during the process.
    """

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

    # create email message
    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header(sender_name, 'utf-8')), sender_email))
    msg['Subject'] = Header(subject, 'utf-8')  # encode the subject with UTF-8

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
        print(f"Error. Unnable to connect server.")
        logger.error(e, exc_info=True)


# function that ensures that user input is non-empty
def get_non_empty_input(prompt: str, min_length: int = None, max_length: int = None):
    """Prompts the user for input until a non-empty response is provided.

    This function repeatedly displays a prompt to the user until a non-empty input is received.
    It ensures that the input is not just whitespace before accepting it.

    :param prompt: The prompt message to display to the user.

    :return: The non-empty user input.
    :rtype: str
    """
    try:
        while True:
            user_input = input(prompt).strip()

            if len(user_input) == 0:
                print("Input cannot be empty. Please try again.")
                continue

            if min_length is not None:
                if 0 < min_length:
                    if min_length < len(user_input):
                        pass
                    else:
                        print(f"Provided value is too short. Min. length is {min_length} digits.")
                        continue
                else:
                    print(f"min_length value cannot be less than 0.")
                    continue

            if max_length is not None:
                if 0 < max_length:
                    if len(user_input) < max_length:
                        pass
                    else:
                        print(f"Provided value is too long. Max length is {max_length} digits.")
                        continue
                else:
                    print(f"max_length value cannot be less than 0.")
                    continue
            return user_input
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None
