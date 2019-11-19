import googlemaps
from pprint import pprint
from datetime import datetime
from googleplaces import GooglePlaces, types, lang
import json

# Reads key and token
with open ('config.json') as f:
    input_keys = json.loads(f.read())
    TOKEN = input_keys['auth']['Bot_Token']
    API_KEY = input_keys['auth']['Google_API_Key']
gmaps = googlemaps.Client(key=API_KEY)
google_places = GooglePlaces(API_KEY)


# Returns the average of a value
def average(l):
    return sum(l) / len(l)

# Removes duplicates from lists
def deduplicate(l):
    return list(set(l))

# Finds the indices of matching locations in results and stored locations
def find_matching_indices(a, b):
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                yield j

# Finds the coordinates of the user's current location 
def find_origin_coordinates(users_address):
    geocode_result = gmaps.geocode(users_address)
    lat_origin = geocode_result[0]['geometry']['location']['lat']
    lng_origin = geocode_result[0]['geometry']['location']['lng']
    origin_coordinates = (lat_origin, lng_origin)
    return origin_coordinates

# Formats query results for comparison, format is (name + address)
# google_locations_ids has the list of the query result from Google Maps API
def format_query_results(query_result):
    google_locations_ids = []
    for i in range (len(query_result.places)):
        query_result.places[i].get_details()
        location_id = query_result.places[i].name + query_result.places[i].formatted_address
        google_locations_ids.append(location_id)
    return google_locations_ids

# Finds the average of previous stored ratings for a specific location 
# averages_of_ratings has the average ratings of all stored locations on the drive 
def find_averages_of_ratings(indicies, google_locations_ids, stored_ratings, chat_id):
    averages_of_ratings = []
    for i in range(len(indicies)):
        location = google_locations_ids[indicies[i]]
        ratings = stored_ratings[chat_id][location]
        average_of_rating = average(ratings)
        averages_of_ratings.append(average_of_rating)
    return averages_of_ratings

# Prompts the user for their location and maximum distance from their origin.
def get_nearest_location(users_address, radius_in_metres, chat_id, stored_ratings, location_type):
    query_result = google_places.nearby_search(location=users_address, radius=int(radius_in_metres), types=[location_type])
    origin_coordinates = find_origin_coordinates(users_address)

    # Initializing variables
    distances = [] # Distances of Google API results from the origin
    destinations = [] # A list of Google API results coordinates 
    google_locations_ids = []# A list of locaations from the query result of the Google API
    averages_of_ratings = []# A of the average ratings of all stored locations on the drive 

    # Puts stored locations in a list for comparison with Google API results 
    stored_locations_ids = list(stored_ratings[chat_id])
   
    google_locations_ids = format_query_results(query_result)
    google_locations_ids = deduplicate(google_locations_ids)

    list(find_matching_indices(stored_locations_ids, google_locations_ids))
    indicies = list(find_matching_indices(stored_locations_ids, google_locations_ids))
    
    averages_of_ratings = find_averages_of_ratings(indicies, google_locations_ids, stored_ratings, chat_id)

    # Create a list of distances of locations from the origin
    for i in range(len(query_result.places)):
        lat_destination = query_result.places[i].geo_location['lat']
        lng_destination = query_result.places[i].geo_location['lng']
        destination_coordinates =  (lat_destination,lng_destination) 
        destinations.append(destination_coordinates)
        distance_details = gmaps.distance_matrix(origin_coordinates,destination_coordinates)
        distance = distance_details['rows'][0]['elements'][0]['distance']['value']
        distances.append(distance)

    # Adjust distances according to previously stored ratings 
    for i in range(len(indicies)):
        distances[indicies[i]] = distances[indicies[i]] * (5 / averages_of_ratings[i])
    
    # Find shortest distance from the origin 
    min_distance = distances.index(min(distances))
    query_result.places[min_distance].get_details()
    places_dict = {
        "location_for_user" : " ".join(list(("Your destination should be ",\
        query_result.places[min_distance].name, " at " , query_result.places[min_distance].formatted_address ,\
        " Their phone number is " , query_result.places[min_distance].local_phone_number , " and their rating is ",\
        str(query_result.places[min_distance].rating)))),
        "location_id" : query_result.places[min_distance].name + query_result.places[min_distance].formatted_address
    }
    return places_dict 
