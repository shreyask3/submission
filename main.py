import requests
from flask import Flask, request, jsonify
import pandas as pd
from geopy.geocoders import Nominatim
from sklearn.metrics.pairwise import haversine_distances
from math import radians, sin, cos, sqrt, atan2

restaurant_data = pd.read_csv('recommendation_system.csv')
restaurant_data = restaurant_data.dropna(subset=['city'])
restaurant_data = restaurant_data.dropna(subset=['latitude'])

geolocator = Nominatim(user_agent="restaurant_recommendation")



def calculate_distance1(user_coords, restaurant_coords):
    result = haversine_distances([user_coords, restaurant_coords])
    return result[0][1] * 6371  

def calculate_distance(user_coords, restaurant_coords):
    user_lat, user_lon = radians(float(user_coords[0])), radians(float(user_coords[1]))
    restaurant_lat, restaurant_lon = radians(float(restaurant_coords[0])), radians(float(restaurant_coords[1]))

    dlon = restaurant_lon - user_lon
    dlat = restaurant_lat - user_lat
    a = (sin(dlat/2)**2 + cos(user_lat) * cos(restaurant_lat) * sin(dlon/2)**2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371 * c  
    return distance

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello world!  Your web application is working!"

@app.route('/Recommend', methods=['GET'])
def get_Recommendation():
    user_address = request.args.get('user_address')
    if not user_address:
        return jsonify({"error": "user_address parameter is required"}), 400

    user_location = geolocator.geocode(user_address)
    if not user_location:
        return jsonify({"error": "Unable to geolocate user address"}), 400

    user_coords = (user_location.latitude, user_location.longitude)
    
    restaurant_data['distance'] = restaurant_data.apply(lambda row: calculate_distance(user_coords, [row['latitude'], row['longitude']]), axis=1)
    
    top_restaurants = restaurant_data.sort_values(by='distance').head(5)
    
    return top_restaurants.to_json(orient='records')

@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
  return send_from_directory('.', 'ai-plugin.json', mimetype='application/json')

@app.route('/openapi.yaml')
def serve_openapi_yaml():
  return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
