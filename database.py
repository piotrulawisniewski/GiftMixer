#GiftMixer project
#R32NOR | ZOLCBYTERS
#2024

### DATABASES ###
# script with all the stuff related to databases within GiftMixer project

# connection to database:
import configparser
import os
import mysql.connector

# pull data are in file under filepath: ~/config/ignored/config.ini, to cover sensitive data
config_file_path = os.path.expanduser("config/ignored/config.ini")
# parse the configuration file
config = configparser.ConfigParser()
config.read(config_file_path)

# Function for creating database for the project:
def database_creation():

    # retrive info from config file
    host = config['gmdatabase']['host']
    user = config['gmdatabase']['user']
    password = config['gmdatabase']['password']

    # connection to MySQL server:
    gmdb = mysql.connector.connect(
        host = host,
        user = user,
        password = password
    )
    cursor = gmdb.cursor()

    # Creating database for the project
    try:
        database = config['gmdatabase']['database']
        cursor.execute("CREATE DATABASE", (database,))
    except:
        pass

    # closing cursor and server connection
    if cursor:
        cursor.close()
    if gmdb:
        gmdb.close()

# Function for turn on connection to database:
def db_switch_on():
    """FUNCTION: turn on connection to database
           :param None
           :return db_connection

           """
    # retrive info from config file
    host = config['gmdatabase']['host']
    user = config['gmdatabase']['user']
    password = config['gmdatabase']['password']
    database = config['gmdatabase']['database']

    # connection to MySQL server:
    db_connection = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database
    )
    return db_connection

# Function for turn on connection to database":
def db_switch_off(db_connection, cursor):
    """FUNCTION: turn off connection to database
           :param cursor, database connection
           :return none
           """
    db_connection.commit()  # Confirming changes into database- just in case ;)

    # closing cursor and server connection
    if cursor:
        cursor.close()
    if db_connection:
        db_connection.close()

# Function for creating tables:
def creating_tables(db_connection, cursor):
    try:
        cursor.execute("CREATE TABLE users (\
                       userID INT unsigned not null AUTO_INCREMENT,\
                       userNick VARCHAR(50) UNIQUE,\
                       userMail VARCHAR(100) NOT NULL UNIQUE,\
                       created_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                       modified_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\
                       created_at_pyTimestamp DATETIME,\
                       modified_at_pyTimestamp DATETIME,\
                       UTC_created_at_pyTimestamp DATETIME,\
                       UTC_modified_at_pyTimestamp DATETIME,\
                       PRIMARY KEY(userID)\
                       ) AUTO_INCREMENT=100000000"
                       )
    except:
        pass

    # Creating passwords table in database for contain users data
    try:
        cursor.execute("CREATE TABLE passwords (\
                               userID INT unsigned,\
                               userPassword VARCHAR(255) NOT NULL,\
                               created_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                               modified_at_dbTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\
                               created_at_pyTimestamp DATETIME,\
                               modified_at_pyTimestamp DATETIME,\
                               UTC_created_at_pyTimestamp DATETIME,\
                               UTC_modified_at_pyTimestamp DATETIME,\
                               PRIMARY KEY (userID),\
                               FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE);"
                       )
    except:
        pass

    # Creating groups table in database for contain groups
    try:
        cursor.execute("CREATE TABLE groups_table (\
                       groupID INT unsigned NOT NULL AUTO_INCREMENT,\
                       groupName VARCHAR(50) NOT NULL UNIQUE,\
                       groupPIN VARCHAR(100),\
                       adminID INT unsigned, \
                       price_limit VARCHAR(50), \
                       place VARCHAR(150), \
                       meetingDate DATETIME NOT NULL, \
                       deadline DATETIME NOT NULL, \
                       remarks VARCHAR(255),\
                       usersFinished INT,\
                       giver_object JSON,\
                       PRIMARY KEY(groupID),\
                       FOREIGN KEY (adminID) REFERENCES users(userID) ON DELETE SET NULL\
                       ) AUTO_INCREMENT = 200000000;"
                       )
    except:
        pass

    cursor.execute("\
    CREATE TABLE IF NOT EXISTS group_members( \
    groupID INT unsigned,\
    userID INT unsigned,\
    groupName VARCHAR(50) NOT NULL,\
    gift_1 JSON,\
    gift_2 JSON,\
    gift_3 JSON,\
    number_of_gifts INT,\
    gifts_to_buy JSON,\
    PRIMARY KEY (groupID, userID),\
    FOREIGN KEY (groupID) REFERENCES groups_table (groupID),\
    FOREIGN KEY (userID) REFERENCES users (userID)\
    )")

    db_connection.commit()


# Functions calling
if __name__ == "__main__":
    database_creation()
    db_connection = db_switch_on()
    cursor = db_connection.cursor()
    creating_tables(db_connection, cursor)
    db_switch_off(db_connection, cursor)


# FUTURE IMPROVEMENTS:

'''
[1] rewrite all database stuff using SQLAlchemy


'''


