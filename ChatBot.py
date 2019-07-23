import time 
import googlemaps 
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
from GoogleAPI import get_nearest_location
import pdb 
from telepot.delegate import pave_event_space, per_chat_id, create_open
import json 
import os.path
import sys
from datetime import datetime
import sys
import asyncio
import random
import telepot
import telepot.aio


#Constants and initializing variables
FILE_NAME = "StoredRatings.txt"
TOKEN = '739707484:AAEme6P0J6aRkBDJeNNfOR_grzeVvmA5in8'
chat_id = 0
API_KEY = 'AIzaSyAMp0_hihUrY3SGqYYahMv56E3EvzrjAT0'
gmaps = googlemaps.Client(key=API_KEY)

#Reads data on the drive
def read_ratings(file_name):
    if not os.path.isfile(FILE_NAME): #If the file doesn't exist
        stored_ratings = {}
    with open (FILE_NAME) as f: #If the file exists 
        stored_ratings = json.loads(f.read())
        return stored_ratings

# Saves new data on the drive
def write_ratings(stored_ratings): 
    file = open(FILE_NAME, "w")
    encoded_dict = json.dumps(stored_ratings)
    file.write(encoded_dict)
    file.close()

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self.state = 'prompt for address'


    #Prompts user for the origin's address
    def prompt_for_address(self, msg):
        self.sender.sendMessage('Please enter your address')
        self.state = 'address received'
        print(msg)
        return self.state

    #Prompts user for the maximum radius
    def prompt_for_radius(self, msg):
        #self.users_address = msg['text']
        print(msg)
        #address_check = gmaps.geocode(msg['text'])
        #if address_check ==  []:
            #self.state = 'address received'
            #self.sender.sendMessage('Invalid address, please try again')
        #else:   
            #self.state = 'prompt for radius'
            #self.sender.sendMessage('Please indicate the maximum distance (in metres) you are willing to travel')
        return self.state

    #Prompts user for their rating of the location
    def prompt_for_rating(self, msg):
        print(msg)
        stored_ratings = read_ratings(FILE_NAME)
        while True:
            try:
                self.radius_in_metres = int(msg['text'])
                chat_id = str(telepot.glance(msg)[2])
                nearest_location = get_nearest_location(self.users_address, self.radius_in_metres, chat_id, stored_ratings)
                self.sender.sendMessage(nearest_location['location_for_user'])
                self.sender.sendMessage('How would you rate your visit from 0 to 5?')
                self.state = 'prompt for rating'
                break
            except ValueError:
                self.state = 'prompt for radius'
                self.sender.sendMessage('invalid radius, please try again')
                break
        return self.state

    def store_rating(self, stored_ratings, location_id, user_rating):
        if chat_id not in stored_ratings:
            stored_ratings[chat_id] = {}
        user_stored_ratings = stored_ratings[chat_id]
        if location_id not in user_stored_ratings:
            user_stored_ratings[location_id] = []
        user_stored_ratings[location_id].append(user_rating)
        write_ratings(stored_ratings)

    #Stores the user's rating 
    def check_rating(self, msg):
        stored_ratings = read_ratings(FILE_NAME)
        while True:
            try:
                user_rating = int(msg['text'])
                if user_rating <= 5 and user_rating >= 0:
                    chat_id = str(telepot.glance(msg)[2])
                    location_id = get_nearest_location(self.users_address, self.radius_in_metres, chat_id, stored_ratings)['location_id']
                    self.store_rating( stored_ratings, location_id, user_rating)
                    # if chat_id not in stored_ratings:
                    #     stored_ratings[chat_id] = {}
                    # user_stored_ratings = stored_ratings[chat_id]
                    # if location_id not in user_stored_ratings:
                    #     user_stored_ratings[location_id] = []
                    # user_stored_ratings[location_id].append(user_rating)
                    # write_ratings(stored_ratings)
                    self.sender.sendMessage('Please enter a new address if you want to use the bot again')
                    self.state = 'address received'
                else:
                    self.state = 'prompt for rating'
                    self.sender.sendMessage('Invalid rating, please try again')
                break
            except ValueError:
                self.state = 'prompt for rating'
                self.sender.sendMessage('Invalid rating, please try again')
                break
        return self.state
    
    #Terminates the bot
    def terminate_bot(self, msg):
        self.sender.sendMessage('Thanks for using the bot. To reuse the bot please type /start have a good day!')
        self.state = 'prompt for address'
        return self.state

    #Handles the states
    def on_chat_message(self, msg):
        if msg == '/start' or self.state == 'prompt for address':
            self.prompt_for_address(msg)
        elif self.state == 'address received':
            self.prompt_for_radius(msg)
        elif self.state == 'prompt for radius' and msg['text'] != '/stop':
            self.prompt_for_rating(msg)
        elif self.state == 'prompt for rating' and msg['text'] != '/stop':
            self.check_rating(msg)
        elif msg['text'] == '/stop':
            self.terminate_bot(msg)
    

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=1000000),
])
MessageLoop(bot).run_as_thread()
print('listening...')

# Keeps the bot running
while 1: 
    time.sleep(100000)
