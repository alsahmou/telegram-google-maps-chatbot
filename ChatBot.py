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
from configparser import ConfigParser

# Reading key and token
with open ('config.json') as f:
    input_keys = json.loads(f.read())
    TOKEN = input_keys['auth']['Bot_Token']
    API_KEY = input_keys['auth']['Google_API_Key']

# List of places types that a user can input
places_types = ['accounting', 'airport', 'amusement_park',
    'aquarium', 'art_gallery', 'atm', 'bakery', 'bank', 'bar', 
    'beauty_salon', 'bicycle_store', 'book_store', 'bowling_alley', 
    'bus_station', 'cafe', 'campground', 'car_dealer', 'car_rental',
    'car_repair', 'car_wash', 'casino', 'cemetery', 'city_hall', 'clothing_store',
    'convenience_store', 'court_house', 'dentist', 'department_store', 'doctor', 
    'electrician', 'electronics_store', 'embassy', 'fire_station', 'florist', 
    'funeral_home', 'furniture_store', 'gas_station', 'gym', 'hair_care', 'hardware_store', 
    'hindu_temple', 'home_goods_store', 'hospital', 'insurance_agency', 'jewelry_store', 'laundry', 
    'lawyer', 'library', 'liquor_store', 'local_government_office', 'locksmith', 'lodging',
    'meal_delivery', 'meal_takeaway', 'mosque', 'movie_rental', 'movie_theatre', 'moving_company',
    'museum', 'night_club', 'painter', 'park', 'parking', 'pet_store', 'pharmacy', 'physiotherapist',
    'plumber', 'police', 'post_office', 'real_estate_agency', 'restaurant', 'roofing_contractor',
    'rv_park', 'school', 'shoe_store', 'shopping_mal', 'spa', 'stadium', 'storage', 'store', 
    'subway_station', 'supermarket', 'synagogue', 'taxi_stand', 'train_station', 'travel_agency',
    'veterinary_care', 'zoo']


# Constants and initializing variables
FILE_NAME = "StoredRatings.txt"
chat_id = 0
gmaps = googlemaps.Client(key=API_KEY)

# Reads data on the drive
def read_ratings(file_name):
    if not os.path.isfile(FILE_NAME): # If the file doesn't exist
        stored_ratings = {}
        return stored_ratings
    with open (FILE_NAME) as f: # If the file exists 
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
        self.state = 'prompt for type'

    # Prompts user for the location type:
    def prompt_for_type(self, msg):
        self.sender.sendMessage('What kind of location are you looking for? Enter types of locations such as (restaurant, gas_station, pharmacy),\
        if the types has more than 1 word, please enter it using an underscore such as (gas_station)')
        self.state = 'type received'
        return self.state

    # Prompts user for the origin's address
    def prompt_for_address(self, msg):
        if msg['text'].lower() in places_types:
            self.location_type = msg['text'].lower()
            self.sender.sendMessage('Please share your location')
            self.state = 'address received'
        else: 
            self.sender.sendMessage('Incorrect location type, please try again')
            self.state = 'type received'
        return self.state

    # Prompts user for the maximum radius
    def prompt_for_radius(self, msg):
        self.users_address_longitude = msg['location']['longitude']
        self.users_address_latitude = msg['location']['latitude']
        self.users_address = gmaps.reverse_geocode((self.users_address_latitude, self.users_address_longitude))
        self.users_address = self.users_address[0]['formatted_address']
        self.sender.sendMessage('Please indicate the maximum distance (in metres) that you are willing to travel')
        self.state = 'radius received'
        return self.state

    # Prompts user for their rating of the location
    def prompt_for_rating(self, msg):
        stripped_radius = msg['text'].strip()
        if str.isnumeric(stripped_radius) == True:
            self.radius_in_metres = int(msg['text'])
            chat_id = str(telepot.glance(msg)[2])
            nearest_location = get_nearest_location(self.users_address, self.radius_in_metres, chat_id, stored_ratings, self.location_type)
            self.sender.sendMessage(nearest_location['location_for_user'])
            self.sender.sendMessage('How would you rate your visit from 1 to 5?')
            self.state = 'rating received'
        else:
            self.state = 'radius received'
            self.sender.sendMessage('Invalid radius, please try again')
            return self.state

    # Formats the user's rating to a dictionary to be stored on the drive later
    def store_rating(self, stored_ratings, location_id, user_rating):
        if chat_id not in stored_ratings:
            stored_ratings[chat_id] = {}
        user_stored_ratings = stored_ratings[chat_id]
        if location_id not in user_stored_ratings:
            user_stored_ratings[location_id] = []
        user_stored_ratings[location_id].append(user_rating)
        write_ratings(stored_ratings)

    # Stores the user's rating  on the drive
    def store_check_ratings(self, msg):
        stripped_rating = msg['text'].strip()
        if str.isnumeric(stripped_rating) == True and int(msg['text']) <= 5 and int(msg['text']) >1:
            user_rating = int(msg['text'])
            chat_id = str(telepot.glance(msg)[2])
            location_id = get_nearest_location(self.users_address, self.radius_in_metres, chat_id, stored_ratings,self.location_type)['location_id']
            self.store_rating( stored_ratings, location_id, user_rating)
            self.sender.sendMessage('Please share a new address if you want to use the bot again')
            self.state = 'address received'
        else: 
            self.state = 'rating received'
            self.sender.sendMessage('Invalid rating, please try again')
        return self.state
    
    # Terminates the bot
    def terminate_bot(self, msg):
        self.sender.sendMessage('Thanks for using the bot. To reuse the bot please type /start. Have a good day!')
        return 

    # Handles the states
    def on_chat_message(self, msg):
        if 'text' in msg and msg['text'] == '/stop':
            self.terminate_bot(msg)
        elif msg == '/start' or self.state == 'prompt for type':
            self.prompt_for_type(msg)
        elif self.state == 'type received':
            self.prompt_for_address(msg)
        elif self.state == 'address received':
            self.prompt_for_radius(msg)
        elif self.state == 'radius received':
            self.prompt_for_rating(msg)
        elif self.state == 'rating received':
            self.store_check_ratings(msg)

    
stored_ratings = read_ratings(FILE_NAME)

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=1000000),
])
MessageLoop(bot).run_as_thread()
print('listening...')

# Keeps the bot running
while 1: 
    time.sleep(100000)
