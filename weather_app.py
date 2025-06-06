import streamlit as st
import requests
from geopy.geocoders import Nominatim
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, Date as SQLDate
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import os
from dotenv import load_dotenv

# Configuration
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
Base = declarative_base()
engine = create_engine("sqlite:///weather.db")
Session = sessionmaker(bind=engine)
session = Session()

# Database Model
class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(Integer, primary_key=True)
    location = Column(String)
    date = Column(SQLDate)
    temperature = Column(Float)
    description = Column(String)

Base.metadata.create_all(engine)

# Helper Functions
def get_ip_location():
    try:
        res = requests.get("https://ipinfo.io/json")
        loc = res.json()["loc"].split(",")
        return float(loc[0]), float(loc[1])
    except:
        return None, None

def geocode_location(user_input):
    geolocator = Nominatim(user_agent="weather_app")
    try:
        if "," in user_input and all(x.strip().replace('.', '', 1).replace('-', '', 1).isdigit() for x in user_input.split(",")):
            lat, lon = map(float, user_input.split(","))
            return lat, lon
        location = geolocator.geocode(user_input)
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def format_weather(weather):
    temp = weather["main"]["temp"]
    desc = weather["weather"][0]["description"].title()
    icon = weather["weather"][0]["icon"]
    humidity = weather["main"]["humidity"]
    wind = weather["wind"]["speed"]
    city = weather.get("name", "Unknown")
    return {
        "temp": temp,
        "desc": desc,
        "icon": f"http://openweathermap.org/img/wn/{icon}@2x.png",
        "humidity": humidity,
        "wind": wind,
        "city": city
    }

def get_daily_forecast(forecast_data):
    forecast_dict = {}
    for entry in forecast_data["list"]:
        date = entry["dt_txt"].split(" ")[0]
        if date not in forecast_dict:
            forecast_dict[date] = entry
    return forecast_dict

# Streamlit UI
st.set_page_config(page_title="🌤️ Weather App with Forecast + DB", layout="centered")
st.title("🌦️ Weather App with Forecast & CRUD")
st.write("Enter a city, landmark, zip code, or coordinates (e.g., `28.6139,77.2090`), or leave blank to use your current location.")

menu = st.sidebar.radio("Menu", ["Live Weather", "Create Record", "Read Records", "Update Record", "Delete Record"])

if menu == "Live Weather":
    user_input = st.text_input("Enter Location:", "")
    if st.button("Get Weather"):
        lat, lon = geocode_location(user_input) if user_input.strip() else get_ip_location()

        if lat and lon:
            weather_data = get_weather(lat, lon)
            forecast_data = get_forecast(lat, lon)

            if "main" in weather_data:
                w = format_weather(weather_data)
                st.subheader(f"Current Weather in {w['city']}")
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(w["icon"])
                with col2:
                    st.metric("Temperature", f"{w['temp']}°C")
                    st.write(f"**Condition:** {w['desc']}")
                    st.write(f"**Humidity:** {w['humidity']}%")
                    st.write(f"**Wind Speed:** {w['wind']} m/s")

                st.markdown("---")
                st.subheader("5-Day Forecast")
                forecast_days = get_daily_forecast(forecast_data)
                for date, data in list(forecast_days.items())[:5]:
                    icon_url = f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"].title()
                    st.markdown(f"**{date}** — {desc}, 🌡️ {temp}°C")
                    st.image(icon_url, width=60)
            else:
                st.error("Could not fetch weather data.")
        else:
            st.error("Could not find that location.")

elif menu == "Create Record":
    st.subheader("Add Weather Record to DB")
    location = st.text_input("Location")
    selected_date = st.date_input("Date", min_value=date(2020, 1, 1), max_value=date.today())
    if st.button("Save Record"):
        lat, lon = geocode_location(location)
        if lat and lon:
            w = get_weather(lat, lon)
            if "main" in w:
                rec = WeatherRecord(
                    location=location,
                    date=selected_date,
                    temperature=w["main"]["temp"],
                    description=w["weather"][0]["description"]
                )
                session.add(rec)
                session.commit()
                st.success("Record saved to database!")
            else:
                st.error("Could not fetch weather data.")
        else:
            st.error("Invalid location.")

elif menu == "Read Records":
    st.subheader("All Records")
    records = session.query(WeatherRecord).all()
    if records:
        df = pd.DataFrame([{
            "ID": r.id,
            "Location": r.location,
            "Date": r.date,
            "Temperature": r.temperature,
            "Description": r.description
        } for r in records])
        st.dataframe(df)
        if st.button("Export to CSV"):
            df.to_csv("weather_data.csv", index=False)
            st.success("Data exported as weather_data.csv")
    else:
        st.info("No records found.")

elif menu == "Update Record":
    st.subheader("Update Record")
    ids = [r.id for r in session.query(WeatherRecord.id).all()]
    if ids:
        record_id = st.selectbox("Select ID to Update", ids)
        rec = session.query(WeatherRecord).get(record_id)
        new_temp = st.number_input("New Temperature", value=rec.temperature)
        new_desc = st.text_input("New Description", value=rec.description)
        if st.button("Update"):
            rec.temperature = new_temp
            rec.description = new_desc
            session.commit()
            st.success("Record updated!")
    else:
        st.info("No records to update.")

elif menu == "Delete Record":
    st.subheader("Delete Record")
    ids = [r.id for r in session.query(WeatherRecord.id).all()]
    if ids:
        record_id = st.selectbox("Select ID to Delete", ids)
        if st.button("Delete"):
            session.delete(session.query(WeatherRecord).get(record_id))
            session.commit()
            st.warning("Record deleted.")
    else:
        st.info("No records to delete.")
