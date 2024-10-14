# GiftMixer project
# R32NOR | ZOLCBYTERS
# 2024

# script with all the stuff related to databases within GiftMixer project

# connection to database:
import configparser
import os
import mysql.connector
from mysql.connector import ProgrammingError

from logger_config import logger, logger_withDisplay

# pull data are in file under filepath: ~/config/ignored/config.ini, to cover sensitive data
config_file_path = os.path.expanduser("config/ignored/config.ini")
config = configparser.ConfigParser()

# parse the configuration file
config.read(config_file_path)

# max length of price input
price_max_len = 50


# Establish connection to MySQL and create a project database
def database_creation():
    """Creates a project database using information from a configuration file.

    This function retrieves MySQL connection details from a configuration file and establishes a connection
    to the MySQL server. It attempts to create a database for the project, handling any errors that may occur
    during the creation process.
    After the database creation attempt, the connection and cursor are closed.

    :return: None
    """
    try:
        # retrieve MySQL credentials from config file
        host = config['gmdatabase']['host']
        user = config['gmdatabase']['user']
        password = config['gmdatabase']['password']

        # establish connection to MySQL server
        gmdb = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = gmdb.cursor()

        # attempt to create a database for the project
        database_name = config['gmdatabase']['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")

    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
    except FileNotFoundError as err:
        log_msg = (f"Configuration file not found: {config_file_path}")
        logger.error(err, log_msg)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
    finally:
        # close the cursor and MySQL server connection
        if cursor:
            cursor.close()
        if gmdb:
            gmdb.close()


# Establish and return a connection to the project database
def db_switch_on():
    """Establishes a connection to the MySQL database using credentials from a configuration file.

    This function retrieves the necessary MySQL connection details from a configuration file,
    establishes a connection to the specified database, and returns the connection object.

    :return: The MySQL database connection object.
    :rtype: mysql.connector.connection.MySQLConnection
    """

    try:
        # retrieve MySQL credentials from config file
        host = config['gmdatabase']['host']
        user = config['gmdatabase']['user']
        password = config['gmdatabase']['password']
        database = config['gmdatabase']['database']

        # establish connection to the MySQL server and specified database
        db_conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        # return the established database connection
        return db_conn

    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Close the database connection and cursor
def db_switch_off(db_conn, crsr):
    """
    Commits pending changes and closes the provided database connection and cursor.

    This function ensures that any pending transactions are committed to the database,
    and it safely closes the cursor and connection, preventing any open handles.

    :param db_conn: The database connection object.
    :type db_conn: mysql.connector.connection.MySQLConnection
    :param crsr: The cursor object associated with the database connection.
    :type crsr: mysql.connector.cursor.MySQLCursor
    :return: None
    """

    # commit any pending changes to the database
    db_conn.commit()  # confirming changes in the database just in case

    # safely close the cursor if it exists
    if crsr:
        crsr.close()

    # safely close the database connection if it exists
    if db_conn:
        db_conn.close()


# Function for creating tables in the database
def creating_tables(db_conn, cursorx):
    """Creates necessary tables in the database for users, passwords, groups, and group members.

    This function defines the schema for the users, passwords, groups_table, and group_members tables.
    It attempts to create each table, and if it already exists, the function bypasses creation without raising an error.

    :param db_conn: The database connection object.
    :type db_conn: mysql.connector.connection.MySQLConnection
    :param cursorx: The cursor object for executing SQL queries.
    :type cursorx: mysql.connector.cursor.MySQLCursor
    :return: None
    """

    try:
        # attempt to create the 'users' table
        try:
            cursorx.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    userID INT unsigned NOT NULL AUTO_INCREMENT,
                    userNick VARCHAR(50) UNIQUE,
                    userMail VARCHAR(100) NOT NULL UNIQUE,
                    created_at_pyTimestamp_UTC DATETIME,
                    modified_at_pyTimestamp_UTC DATETIME,
                    created_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY(userID)
                ) AUTO_INCREMENT=100000000;
            """)
        except ProgrammingError as err:
            print(f"Table already exists.")
            logger.error(err, exc_info=True)


        # attempt to create the 'passwords' table
        try:
            cursorx.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    userID INT unsigned,
                    userPassword VARCHAR(255) NOT NULL,
                    salt BINARY(16),
                    created_at_pyTimestamp_UTC DATETIME,
                    modified_at_pyTimestamp_UTC DATETIME,
                    created_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (userID),
                    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE
                );
            """)
        except ProgrammingError as err:
            print(f"Table already exists.")
            logger.error(err, exc_info=True)

        # attempt to create the 'groups_table'

        global price_max_len

        try:
            cursorx.execute(f"""
                CREATE TABLE IF NOT EXISTS groups_table (
                    groupID INT unsigned NOT NULL AUTO_INCREMENT,
                    groupName VARCHAR(50) NOT NULL,
                    groupPIN INT,
                    adminID INT unsigned,
                    price_limit VARCHAR({price_max_len}),
                    place VARCHAR(150),
                    meetingDate DATETIME NOT NULL,
                    deadline DATETIME NOT NULL,
                    eventTimezone VARCHAR(50),
                    remarks VARCHAR(255),
                    usersFinished INT,
                    giver_object JSON,
                    PRIMARY KEY(groupID),
                    FOREIGN KEY (adminID) REFERENCES users(userID) ON DELETE SET NULL
                ) AUTO_INCREMENT=200000000;
            """)
        except ProgrammingError as err:
            print(f"Table already exists.")
            logger.error(err, exc_info=True)

        # attempt to create the 'group_members' table

        try:
            cursorx.execute("""
                CREATE TABLE IF NOT EXISTS group_members (
                    groupID INT unsigned,
                    userID INT unsigned,
                    groupName VARCHAR(50) NOT NULL,
                    gift_1 JSON,
                    gift_2 JSON,
                    gift_3 JSON,
                    number_of_gifts INT,
                    gifts_to_buy JSON,
                    PRIMARY KEY (groupID, userID),
                    FOREIGN KEY (groupID) REFERENCES groups_table(groupID),
                    FOREIGN KEY (userID) REFERENCES users(userID)
                );
            """)
        except ProgrammingError as err:
            print(f"Table already exists.")
            logger.error(err, exc_info=True)


        # commit changes to the database
        db_conn.commit()

    except mysql.connector.Error:
        log_msg = ('Database error.')
        logger_withDisplay.warning(log_msg)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)


# Functions calling
if __name__ == "__main__":
    try:
        database_creation()
        db_connection = db_switch_on()
        cursor = db_connection.cursor()
        creating_tables(db_connection, cursor)
        db_switch_off(db_connection, cursor)
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
