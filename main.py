# #GiftMixer project
# #R32NOR|anklebiters
# #2024
#
# """GiftMixer is a script that helps to split Christmas wishes to people in group.
# One person buys only one present for only one person in the group. The reason for build it was to get one bigger gift than few smaller.
# It prevents too much consumption, saves time on pre-christmas rush and helps to spent money wisely. """

# importing modules
import mysql.connector
import re

# importing scripts
import login # file with login, register and account management functions:
print('\nWelcome to Gift Mixer!')
print('A free tool that helps to split Christmas (and not only) wishes to people in group, to reduce consumption, save time and avoid pre-christmas gift-fever and headache :) \n ')


def main():

    while True:
        print('\n[1] Sign in \n[2] Register \n[3] Exit')
        program_mode = input('Choose mode : ')

        if program_mode.strip() == '1':    # login- for existing users
            login.login() # launching register function

        elif program_mode.strip() == '2':  # register new user
            login.register() # launching register function

        elif program_mode.strip() == '3':  # exits the program
            break

        else:
            print("Wrong input- choose option 1, 2 or 3.\n")

if __name__ == "__main__":
    main()







