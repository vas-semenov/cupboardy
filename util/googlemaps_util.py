"""
Author: Thomas Reece
Description: This file contains functionalities for interactions with google maps API to display food banks.
"""

import requests

GOOGLE_MAPS_API_KEY = 'AIzaSyAALiJ5omMUZn4pGvsYDvLEePC8NJiZTis'


# Takes location data from the postcode, and returns the latitude and longitude of the location
def get_location_data(postcode):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={postcode}&key={GOOGLE_MAPS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        location = data['results'][0]['geometry']['location']
        return {'latitude': location['lat'], 'longitude': location['lng']}
    else:
        return None


# Takes the latitude and longitude of a location, and returns a list of food banks within 5km
def get_food_banks(latitude, longitude):
    # Set up parameters for nearby search request
    api_key = 'AIzaSyAALiJ5omMUZn4pGvsYDvLEePC8NJiZTis'
    radius = 5000  # 5 kilometers
    keyword = 'food bank'

    # Make a request to Google Places API for nearby food banks
    url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&keyword={keyword}&key={GOOGLE_MAPS_API_KEY}'
    response = requests.get(url)

    # Parse the response and extract food bank data
    if response.status_code == 200:
        data = response.json()
        food_banks = []
        for result in data.get('results', []):
            name = result.get('name', '')
            address = result.get('vicinity', '')
            lat = result.get('geometry', {}).get('location', {}).get('lat', '')
            lng = result.get('geometry', {}).get('location', {}).get('lng', '')
            place_id = result.get('place_id', '')  # Get the place_id
            food_banks.append(
                {'name': name, 'address': address, 'latitude': lat, 'longitude': lng, 'place_id': place_id})
        return food_banks
    else:
        return []


#Takes a place_id and returns the details of the nearby food banks (contact details and website)
def get_food_bank_details(place_id):
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,formatted_phone_number,website&key={GOOGLE_MAPS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            return {
                'name': data['result'].get('name', ''),
                'rating': data['result'].get('rating', ''),
                'phone_number': data['result'].get('formatted_phone_number', ''),
                'website': data['result'].get('website', '')
            }
    return None
