# :gift: GiftMixer


GiftMixer is an intuitive tool that simplifies the process of organizing gift exchanges for friends, families, or colleagues. 
Whether for Christmas, holidays, birthdays, or any special occasion, GiftMixer helps users efficiently manage gift draws, 
ensuring a smooth and enjoyable experience and surprise for all participants.

## :sparkles: Genesis

GiftMixer project comes up as portoflio project both to improve my python skills (instead learning from tutorials)
and to be the showcase for recrutation proccesses.  
From the variety of ideas that are waiting in the queue for implementation I choose this one cause the idea comes from
my own need.  

GiftMixer is a script that helps to split Christmas (but not only) wishes between participants in the group. One person buys only one present for only one person in the group. The reason for build it was to get one bigger gift
than few smaller. It also prevents too much consumption, saves time on pre-christmas rush and helps to spent money wisely.

Long term aim of this project is to run it as a free service under giftmixer.eu domain, to make such gift exchange easier.

## :tada: Features

- Safe register and log-in module ensuring password salting and hashed version storage in database.
- Setting groups for a wish shuffling and disributing between group members with a group managing features for group admins.
- Possibility to send out up to 3 wishes by each user to the group. Wishes can be edited or deleted (if deadline hasn't pass).
- WishAI- AI helper, if user have no idea what to wish.
- Mixing function: fairly pairs participants for a gift exchange, ensuring no one is left out and excludes self-pairing.
- Email sending: users receive messages with wishes of other user on their mail boxes.
- User settings like nick or password change
- Checking eligiblity of inputted values


## :hammer_and_wrench: Tech stack

- Python
- MySQL
- API (Gemini AI)


## :file_folder: Project structure

- <code>main.py</code>: main file that manages the whole project
- <code>database.py</code>: script with all the stuff related to databases within GiftMixer project
- <code>classes.py</code>: stores all classes definitions
- <code>login.py</code>: file with all the registration and log-in logic
- <code>functions.py</code>: all the general purpuse functions
- <code>logger_config.py</code>: configuration of error loggers
- <code>wishAI_Gemini_API.py</code>: script that manages whole connection to Gemini AI via API, setting model with required parameters, and manages acting when prohibided phrase occur
- <code>gemini_API_training_prompt.txt</code>: file for contain plain text with first 'training' prompt for Gemini model to set the context of talk
- <code>config.ini</code>: git ignored file with database, and email server connection parameters


## :memo: Prerequisities

- Python 3.12
- MySQL 8.0.35
- Python modules that have to be installed via pip: 
  - pytz – For handling time zones: pip install pytz
  - mysql.connector – For connecting to MySQL databases: pip install mysql-connector-python
  - tzlocal – For getting the local time zone: pip install tzlocal
  - google-generativeai – For Google’s Generative AI API: pip install google-generativeai  
  

<code>config.ini</code>: For using this project you have to save configuration file placed at: /config/ignored/config.ini  
Data in file should follow below structure:

[gmdatabase]  
host = hostname  
user = username  
password = yourPassword  
database = databaseName

[email]  
host = hostAdress  
port = 587  
sender_email = senderEmail  
sender_name = GiftMixer  
sender_password = emailPassword

<code>environment variables</code>: for using WishAI - ideas helper you have to create an account on Google AI Studio (https://aistudio.google.com/app/apikey), then 'Create API key' and save this key as environment variable in your system under 'GOOGLE_API_KEY' key.


## :rocket: Future Development


#### GiftMixer project will be rewritten with django framework and published under <a>gifmixer.eu</a> domain. Current state was published on github for recrutation purposes.
#### If you fetch the code and using it - have fun! ;)







