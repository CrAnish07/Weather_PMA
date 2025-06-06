import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from db import WeatherRecord
import os
from dotenv import load_dotenv

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def geocode_location(location_text):
    geo = Nominatim(user_agent="weather_crud_app")
    try:
        loc = geo.geocode(location_text)
        return (loc.latitude, loc.longitude, loc.address) if loc else (None, None, None)
    except:
        return None, None, None

def fetch_historical_weather(lat, lon, date):
    timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
    url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()
    try:
        temp = res["current"]["temp"]
        desc = res["current"]["weather"][0]["description"]
        return temp, desc
    except:
        return None, None

def validate_date_range(start, end):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        return start_date <= end_date
    except:
        return False
