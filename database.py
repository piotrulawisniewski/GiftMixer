#GiftMixer project
#R32NOR|anklebiters
#2024

### DATABASES ###
# This file is for database creation and further management.




# connection with database:

gmdb = mysql.connector.connect(
    host ='localhost',
    user = 'root',
    password = 'ojapierdole!',
    database = 'giftmixerdb'
)

cursor = gmdb.cursor()

# # creating database for the project (to turn off/comment when done)
# cursor.execute("CREATE DATABASE giftmixerdb")


# check if database has been added
'''
cursor.execute("SHOW DATABASES")

for x in cursor:
    print(x)
'''

# Database: Create Table 'user'
'''
cursor.execute("CREATE TABLE users (\
               userID INT,\
               userName VARCHAR(50) NOT NULL UNIQUE,\
               userMail VARCHAR(100) NOT NULL UNIQUE,\
               userPassword VARCHAR(255) NOT NULL,\
               PRIMARY KEY(userID)\
               )")
               '''

